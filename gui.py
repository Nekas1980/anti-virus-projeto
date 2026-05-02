import os
import threading
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from config import PATHS, SCAN
from excel_exporter import ExcelReportGenerator
from exclusion_matcher import ExclusionMatcher
from gui_filters import FilterCriteria, filter_results, format_elapsed, format_eta
from hash_cache import HashCache
from notifications import notify_scan_complete
from report_generator import HTMLReportGenerator, ReportMetadata, generate_json_report
from scan_history import ScanHistory
from user_prefs import UserPrefs
from Virus_project import (
    load_exclusions,
    load_signatures,
    quarantine_file,
    save_report,
    scan_file,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

MINT = "#00ffa3"
CRIMSON = "#ff0055"
AMBER = "#ffb347"
BG_DARK = "#030503"
SURFACE = "#0d140d"
TEXT_MAIN = "#e8f5e8"
MUTED = "#8fa88f"

UI_REFRESH_EVERY = 25  # ficheiros entre actualizações de progress/UI


class CyberSentinelGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CYBER-SENTINEL // PROJETO ANTIVÍRUS 2026")
        self.geometry("1200x820")
        self.configure(fg_color=BG_DARK)

        self.prefs = UserPrefs(PATHS["user_prefs"])
        self.history = ScanHistory(PATHS["scan_history"])
        self.cache = HashCache(PATHS["scan_cache"]) if SCAN["cache_enabled"] else None

        self.pasta_alvo = ctk.StringVar()
        if self.prefs.recent_paths:
            self.pasta_alvo.set(self.prefs.recent_paths[0])

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh_results_view())
        self.show_clean_var = ctk.BooleanVar(value=True)
        self.show_infected_var = ctk.BooleanVar(value=True)
        self.show_skipped_var = ctk.BooleanVar(value=False)

        self.total_ficheiros = 0
        self.infectados = 0
        self.limpos = 0
        self.ignorados = 0
        self.results = []
        self.last_metadata: ReportMetadata | None = None
        self.last_report_html: Path | None = None

        self._scan_active = False
        self._pause_event = threading.Event()
        self._pause_event.set()  # set = running, clear = paused
        self._cancel_flag = False

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.setup_ui()

    def _on_close(self):
        self._cancel_flag = True
        self._pause_event.set()
        if self.cache is not None:
            self.cache.close()
        self.history.close()
        self.destroy()

    # ─────────────────────────────────────────────────────────────────
    # UI construction
    # ─────────────────────────────────────────────────────────────────

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="// CYBER-SENTINEL",
            font=ctk.CTkFont(family="Courier", size=18, weight="bold"),
            text_color=MINT,
        )
        self.logo_label.pack(pady=(30, 30), padx=20)

        self._create_sidebar_button("SCAN PASTA", self.correr_scan)
        self._create_sidebar_button("SCAN RÁPIDO", self.correr_scan_rapido)
        self._create_sidebar_button("SCAN PC COMPLETO", self.correr_scan_pc)

        self.btn_pause = self._create_sidebar_button("⏸ PAUSAR", self._toggle_pause)
        self.btn_pause.configure(state="disabled")

        self._create_sidebar_button("HISTÓRICO", self.mostrar_historico)
        self._create_sidebar_button("LIMPAR LOG", self.reset_interface)

        self.stats_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=20)

        self.lbl_stat_total = self._create_stat_widget(self.stats_frame, "TOTAL", TEXT_MAIN)
        self.lbl_stat_limpos = self._create_stat_widget(self.stats_frame, "LIMPOS", MINT)
        self.lbl_stat_infectados = self._create_stat_widget(self.stats_frame, "AMEAÇAS", CRIMSON)

        # Live metrics
        self.lbl_speed = ctk.CTkLabel(
            self.sidebar,
            text="—",
            font=ctk.CTkFont(family="Courier", size=11),
            text_color=AMBER,
            justify="left",
        )
        self.lbl_speed.pack(fill="x", padx=20, pady=(0, 12))

    def _build_main_area(self):
        self.main_area = ctk.CTkFrame(self, corner_radius=24, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(2, weight=1)

        # Header (path picker)
        self.header_frame = ctk.CTkFrame(
            self.main_area, fg_color=SURFACE, corner_radius=16, height=80
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        self.header_frame.grid_propagate(False)

        self.entry_pasta = ctk.CTkEntry(
            self.header_frame,
            textvariable=self.pasta_alvo,
            placeholder_text="Selecione o diretório para análise...",
            width=500,
            height=40,
            border_color=MINT,
            fg_color=BG_DARK,
        )
        self.entry_pasta.pack(side="left", padx=20, pady=20)

        ctk.CTkButton(
            self.header_frame,
            text="BROWSE",
            width=100,
            command=self.escolher_pasta,
            fg_color=MINT,
            text_color=BG_DARK,
            hover_color=TEXT_MAIN,
            font=ctk.CTkFont(weight="bold"),
        ).pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            self.header_frame,
            text="RECENTES ▼",
            width=110,
            command=self._toggle_recent_menu,
            fg_color="transparent",
            border_width=1,
            border_color=MINT,
            text_color=MINT,
            hover_color=BG_DARK,
        ).pack(side="left", padx=(0, 20))

        # Progress + status row
        progress_row = ctk.CTkFrame(self.main_area, fg_color=SURFACE, corner_radius=16)
        progress_row.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        self.progress_bar = ctk.CTkProgressBar(progress_row, progress_color=MINT, height=12)
        self.progress_bar.pack(fill="x", padx=20, pady=(16, 6))
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(
            progress_row,
            text="PRONTO PARA SCAN",
            font=ctk.CTkFont(family="Courier", size=12),
            text_color=MUTED,
            anchor="w",
        )
        self.lbl_status.pack(fill="x", padx=20, pady=(0, 14))

        # Tabbed area: Log / Resultados / Exportar
        self.tabs = ctk.CTkTabview(
            self.main_area,
            corner_radius=18,
            fg_color=SURFACE,
            segmented_button_selected_color=MINT,
            segmented_button_selected_hover_color=TEXT_MAIN,
        )
        self.tabs.grid(row=2, column=0, sticky="nsew")

        self.tabs.add("LOG")
        self.tabs.add("RESULTADOS")
        self.tabs.add("EXPORTAR")

        self._build_log_tab(self.tabs.tab("LOG"))
        self._build_results_tab(self.tabs.tab("RESULTADOS"))
        self._build_export_tab(self.tabs.tab("EXPORTAR"))

    def _build_log_tab(self, parent):
        self.log_text = ctk.CTkTextbox(
            parent,
            fg_color=BG_DARK,
            text_color=MINT,
            font=ctk.CTkFont(family="Courier", size=13),
            corner_radius=12,
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_results_tab(self, parent):
        controls = ctk.CTkFrame(parent, fg_color="transparent")
        controls.pack(fill="x", padx=10, pady=(10, 6))

        ctk.CTkEntry(
            controls,
            textvariable=self.search_var,
            placeholder_text="Pesquisar por nome ou caminho…",
            border_color=MINT,
            fg_color=BG_DARK,
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkCheckBox(
            controls,
            text="Limpos",
            variable=self.show_clean_var,
            command=self._refresh_results_view,
            fg_color=MINT,
            border_color=MINT,
            text_color=TEXT_MAIN,
        ).pack(side="left", padx=4)
        ctk.CTkCheckBox(
            controls,
            text="Ameaças",
            variable=self.show_infected_var,
            command=self._refresh_results_view,
            fg_color=CRIMSON,
            border_color=CRIMSON,
            text_color=TEXT_MAIN,
        ).pack(side="left", padx=4)
        ctk.CTkCheckBox(
            controls,
            text="Ignorados",
            variable=self.show_skipped_var,
            command=self._refresh_results_view,
            fg_color=AMBER,
            border_color=AMBER,
            text_color=TEXT_MAIN,
        ).pack(side="left", padx=4)

        self.lbl_results_count = ctk.CTkLabel(
            controls, text="0 / 0", text_color=MUTED, font=ctk.CTkFont(size=11)
        )
        self.lbl_results_count.pack(side="left", padx=(10, 0))

        self.results_scroll = ctk.CTkScrollableFrame(parent, fg_color=BG_DARK)
        self.results_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_export_tab(self, parent):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            wrapper,
            text="// EXPORTAÇÃO DE RELATÓRIO",
            text_color=MINT,
            font=ctk.CTkFont(family="Courier", size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            wrapper,
            text=(
                "Os relatórios são guardados em " + str(PATHS["output_dir"])
                + ".\nGera versões adicionais a partir do último scan concluído."
            ),
            text_color=MUTED,
            font=ctk.CTkFont(size=12),
            justify="left",
        ).pack(anchor="w", pady=(0, 16))

        btn_row = ctk.CTkFrame(wrapper, fg_color="transparent")
        btn_row.pack(fill="x")

        for label, command in (
            ("HTML (gráficos)", lambda: self._export("html")),
            ("JSON (estruturado)", lambda: self._export("json")),
            ("EXCEL (.xlsx)", lambda: self._export("xlsx")),
        ):
            ctk.CTkButton(
                btn_row,
                text=label,
                command=command,
                fg_color=MINT,
                text_color=BG_DARK,
                hover_color=TEXT_MAIN,
                font=ctk.CTkFont(weight="bold"),
                height=44,
            ).pack(side="left", padx=(0, 10))

        self.lbl_export_status = ctk.CTkLabel(
            wrapper, text="", text_color=MUTED, font=ctk.CTkFont(size=12)
        )
        self.lbl_export_status.pack(anchor="w", pady=(16, 0))

    def _create_sidebar_button(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(weight="bold"),
            fg_color="transparent",
            border_width=1,
            border_color=MINT,
            text_color=MINT,
            hover_color=BG_DARK,
        )
        btn.pack(fill="x", padx=20, pady=4)
        return btn

    def _create_stat_widget(self, parent, label, color):
        frame = ctk.CTkFrame(parent, fg_color=BG_DARK, corner_radius=12, height=70)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=10), text_color=MUTED).pack(
            pady=(8, 0), padx=15, anchor="w"
        )
        lbl_val = ctk.CTkLabel(
            frame, text="0", font=ctk.CTkFont(size=24, weight="bold"), text_color=color
        )
        lbl_val.pack(padx=15, anchor="w")
        return lbl_val

    # ─────────────────────────────────────────────────────────────────
    # Path picker / recent paths
    # ─────────────────────────────────────────────────────────────────

    def escolher_pasta(self):
        initial = self.prefs.recent_paths[0] if self.prefs.recent_paths else None
        pasta = filedialog.askdirectory(initialdir=initial)
        if pasta:
            self.pasta_alvo.set(pasta)
            self.prefs.add_recent_path(pasta)

    def _toggle_recent_menu(self):
        recent = self.prefs.recent_paths
        if not recent:
            messagebox.showinfo("Recentes", "Sem caminhos recentes ainda.")
            return
        menu = ctk.CTkToplevel(self)
        menu.title("Caminhos recentes")
        menu.geometry("520x320")
        menu.configure(fg_color=BG_DARK)
        ctk.CTkLabel(menu, text="// CAMINHOS RECENTES", text_color=MINT).pack(pady=(15, 5))
        for p in recent:
            ctk.CTkButton(
                menu,
                text=p,
                anchor="w",
                fg_color="transparent",
                text_color=TEXT_MAIN,
                hover_color=SURFACE,
                command=lambda path=p: (self.pasta_alvo.set(path), menu.destroy()),
            ).pack(fill="x", padx=15, pady=2)

    # ─────────────────────────────────────────────────────────────────
    # Logging / state reset
    # ─────────────────────────────────────────────────────────────────

    def adicionar_log(self, texto):
        self.log_text.insert("end", f"{texto}\n")
        self.log_text.see("end")

    def adicionar_log_thread_safe(self, texto):
        self.after(0, self.adicionar_log, texto)

    def reset_interface(self):
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)
        self.lbl_stat_total.configure(text="0")
        self.lbl_stat_limpos.configure(text="0")
        self.lbl_stat_infectados.configure(text="0")
        self.lbl_speed.configure(text="—")
        self.lbl_status.configure(text="PRONTO PARA SCAN")
        self.infectados = 0
        self.limpos = 0
        self.ignorados = 0
        self.results = []
        self.last_metadata = None
        self.last_report_html = None
        self._refresh_results_view()

    # ─────────────────────────────────────────────────────────────────
    # Scan launchers
    # ─────────────────────────────────────────────────────────────────

    def _start_scan(self, pastas):
        if self._scan_active:
            messagebox.showwarning("Scan em curso", "Já existe um scan a decorrer.")
            return
        valid = [p for p in pastas if p.exists()]
        if not valid:
            messagebox.showerror("Erro", "Nenhum dos caminhos seleccionados existe.")
            return
        for p in valid:
            self.prefs.add_recent_path(str(p))
        self.reset_interface()
        threading.Thread(target=self._scan_worker, args=(valid,), daemon=True).start()

    def correr_scan(self):
        pasta = self.pasta_alvo.get()
        if not pasta:
            messagebox.showwarning("Aviso", "Selecione uma pasta primeiro!")
            return
        self._start_scan([Path(pasta)])

    def correr_scan_rapido(self):
        user = os.path.expanduser("~")
        candidatos = [Path(user) / "Downloads", Path(user) / "Desktop"]
        if os.name == "nt":
            candidatos.append(Path("C:/Windows/Temp"))
        self.adicionar_log_thread_safe("// INICIANDO SCAN RÁPIDO PROTOCOL...")
        self._start_scan(candidatos)

    def correr_scan_pc(self):
        user = os.path.expanduser("~")
        candidatos = [
            Path(user) / d for d in ["Downloads", "Desktop", "Documents", "Pictures"]
        ]
        self.adicionar_log_thread_safe("// INICIANDO FULL SYSTEM SCAN PROTOCOL...")
        self._start_scan(candidatos)

    # ─────────────────────────────────────────────────────────────────
    # Pause / resume
    # ─────────────────────────────────────────────────────────────────

    def _toggle_pause(self):
        if not self._scan_active:
            return
        if self._pause_event.is_set():
            self._pause_event.clear()
            self.btn_pause.configure(text="▶ RETOMAR")
            self.lbl_status.configure(text="PAUSADO")
        else:
            self._pause_event.set()
            self.btn_pause.configure(text="⏸ PAUSAR")

    # ─────────────────────────────────────────────────────────────────
    # Scan worker
    # ─────────────────────────────────────────────────────────────────

    def _scan_worker(self, pastas):
        self._scan_active = True
        self._cancel_flag = False
        self._pause_event.set()
        self.after(0, self.btn_pause.configure, {"state": "normal", "text": "⏸ PAUSAR"})

        started_at = time.time()
        try:
            signatures = load_signatures(PATHS["signatures"])
            exclusions = load_exclusions(PATHS["exclusions"])
            matcher = ExclusionMatcher(exclusions)

            todos = []
            for pasta in pastas:
                for p in pasta.rglob("*"):
                    if p.is_file() and not matcher.matches(p):
                        todos.append(p)

            total = len(todos)
            self.after(0, lambda: self.lbl_stat_total.configure(text=str(total)))

            if total == 0:
                self.adicionar_log_thread_safe("!! NENHUM FICHEIRO ENCONTRADO.")
                return

            self.adicionar_log_thread_safe(f"// ANALISANDO {total} FICHEIROS...\n")

            for i, ficheiro in enumerate(todos, 1):
                self._pause_event.wait()  # blocks while paused
                if self._cancel_flag:
                    break
                result = scan_file(ficheiro, signatures, cache=self.cache)
                self.results.append(result)

                if result.status == "infected":
                    self.infectados += 1
                    self.after(
                        0,
                        self.lbl_stat_infectados.configure,
                        {"text": str(self.infectados)},
                    )
                    self.adicionar_log_thread_safe(f"[!] AMEAÇA: {result.file_path}")
                    self.adicionar_log_thread_safe(f"    └─ TIPO: {result.reason}")
                elif result.status == "skip":
                    self.ignorados += 1
                else:
                    self.limpos += 1

                if i % UI_REFRESH_EVERY == 0 or i == total:
                    self._tick_metrics(i, total, started_at)

            metadata = ReportMetadata(
                started_at=started_at,
                finished_at=time.time(),
                paths=[str(p) for p in pastas],
            )
            self.last_metadata = metadata

            json_path = PATHS["output_dir"] / f"scan_{datetime.now():%Y%m%d_%H%M%S}.json"
            html_path = json_path.with_suffix(".html")
            save_report(self.results, json_path)
            HTMLReportGenerator.generate(self.results, html_path, metadata=metadata)
            self.last_report_html = html_path

            self.history.record(
                paths=pastas,
                total=total,
                clean=self.limpos,
                infected=self.infectados,
                skipped=self.ignorados,
                started_at=started_at,
                report_path=html_path,
            )

            self.after(0, self.lbl_stat_limpos.configure, {"text": str(self.limpos)})
            self.adicionar_log_thread_safe(
                "──────────────────────────────────────────────"
            )
            if self._cancel_flag:
                self.adicionar_log_thread_safe("// SCAN CANCELADO.")
                self.after(0, self.lbl_status.configure, {"text": "SCAN CANCELADO"})
            else:
                self.adicionar_log_thread_safe("// SCAN CONCLUÍDO COM SUCESSO.")
                self.after(0, self.lbl_status.configure, {"text": "SCAN CONCLUÍDO"})

            self.after(0, self._refresh_results_view)

            if self.prefs.get("notify_on_complete", True) and not self._cancel_flag:
                notify_scan_complete(self.infectados, self.limpos, self.ignorados)

            if self.infectados > 0 and not self._cancel_flag:
                self.after(0, self._prompt_quarantine)
        finally:
            self._scan_active = False
            self.after(
                0,
                self.btn_pause.configure,
                {"state": "disabled", "text": "⏸ PAUSAR"},
            )

    def _tick_metrics(self, i: int, total: int, started_at: float):
        elapsed = time.time() - started_at
        rate = i / elapsed if elapsed > 0 else 0
        progress = i / total
        eta = format_eta(total - i, rate)
        elapsed_str = format_elapsed(elapsed)

        def update():
            self.progress_bar.set(progress)
            self.lbl_status.configure(
                text=f"ANALISANDO  {i}/{total}  ({int(progress * 100)}%)"
            )
            self.lbl_speed.configure(
                text=f"{rate:.1f} files/s\nELAPSED  {elapsed_str}\nETA      {eta}"
            )

        self.after(0, update)

    # ─────────────────────────────────────────────────────────────────
    # Results view (filterable)
    # ─────────────────────────────────────────────────────────────────

    def _refresh_results_view(self):
        if not hasattr(self, "results_scroll"):
            return
        for child in self.results_scroll.winfo_children():
            child.destroy()

        criteria = FilterCriteria(
            query=self.search_var.get(),
            show_clean=self.show_clean_var.get(),
            show_infected=self.show_infected_var.get(),
            show_skipped=self.show_skipped_var.get(),
        )
        filtered = filter_results(self.results, criteria)

        self.lbl_results_count.configure(
            text=f"{len(filtered)} / {len(self.results)}"
        )

        if not filtered:
            ctk.CTkLabel(
                self.results_scroll,
                text="Sem resultados que correspondam aos filtros.",
                text_color=MUTED,
            ).pack(pady=20)
            return

        for r in filtered[:500]:  # cap visual: 500 linhas
            color = {
                "infected": CRIMSON,
                "skip": AMBER,
                "clean": MINT,
            }.get(r.status, MUTED)

            row = ctk.CTkFrame(self.results_scroll, fg_color=SURFACE, corner_radius=6)
            row.pack(fill="x", pady=2, padx=4)
            badge = r.status.upper().ljust(8)
            text = f"[{badge}] {r.file_path}"
            if r.reason:
                text += f"  · {r.reason}"
            ctk.CTkLabel(
                row,
                text=text,
                anchor="w",
                text_color=color,
                font=ctk.CTkFont(family="Courier", size=12),
            ).pack(fill="x", padx=10, pady=4)

        if len(filtered) > 500:
            ctk.CTkLabel(
                self.results_scroll,
                text=f"+ {len(filtered) - 500} resultados não mostrados (use filtros)",
                text_color=MUTED,
            ).pack(pady=10)

    # ─────────────────────────────────────────────────────────────────
    # Export
    # ─────────────────────────────────────────────────────────────────

    def _export(self, fmt: str):
        if not self.results:
            self.lbl_export_status.configure(
                text="Nenhum scan concluído ainda — corre um scan primeiro.",
                text_color=AMBER,
            )
            return

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = PATHS["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)

        if fmt == "html":
            path = out_dir / f"scan_export_{ts}.html"
            ok = HTMLReportGenerator.generate(self.results, path, metadata=self.last_metadata)
        elif fmt == "json":
            path = out_dir / f"scan_export_{ts}.json"
            ok = generate_json_report(self.results, path, metadata=self.last_metadata)
        elif fmt == "xlsx":
            if not ExcelReportGenerator.is_available():
                self.lbl_export_status.configure(
                    text="openpyxl não instalado — pip install openpyxl",
                    text_color=CRIMSON,
                )
                return
            path = out_dir / f"scan_export_{ts}.xlsx"
            ok = ExcelReportGenerator.generate(
                self.results, path, metadata=self.last_metadata
            )
        else:
            return

        if ok:
            self.lbl_export_status.configure(
                text=f"✓ Exportado: {path}", text_color=MINT
            )
        else:
            self.lbl_export_status.configure(
                text="✗ Falhou exportação — ver logs.", text_color=CRIMSON
            )

    # ─────────────────────────────────────────────────────────────────
    # Quarantine + History
    # ─────────────────────────────────────────────────────────────────

    def _prompt_quarantine(self):
        if messagebox.askyesno(
            "Ameaças Detetadas",
            f"Encontradas {self.infectados} ameaças. Isolar em quarentena?",
        ):
            quarantine_dir = PATHS["quarantine_dir"]
            for r in self.results:
                if r.status == "infected":
                    quarantine_file(Path(r.file_path), quarantine_dir)
            self.adicionar_log("// PROTOCOLO DE QUARENTENA EXECUTADO.")

    def mostrar_historico(self):
        recent = self.history.recent(limit=20)
        win = ctk.CTkToplevel(self)
        win.title("Histórico de Scans")
        win.geometry("780x520")
        win.configure(fg_color=BG_DARK)

        ctk.CTkLabel(
            win,
            text="// HISTÓRICO DE VARREDURAS",
            text_color=MINT,
            font=ctk.CTkFont(family="Courier", size=16, weight="bold"),
        ).pack(pady=(15, 10))

        if not recent:
            ctk.CTkLabel(win, text="Sem scans registados ainda.", text_color=MUTED).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(win, fg_color=SURFACE)
        scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        for record in recent:
            row = ctk.CTkFrame(scroll, fg_color=BG_DARK, corner_radius=8)
            row.pack(fill="x", padx=8, pady=4)

            color = CRIMSON if record.infected > 0 else MINT
            header = (
                f"{record.started_iso}  ·  {record.duration_seconds:.1f}s  ·  "
                f"{record.total} fich.  ·  ✓{record.clean}  ✗{record.infected}"
            )
            ctk.CTkLabel(row, text=header, text_color=color, anchor="w").pack(
                fill="x", padx=12, pady=(8, 0)
            )
            paths_text = "  ".join(record.paths)[:140]
            ctk.CTkLabel(row, text=paths_text, text_color=MUTED, anchor="w").pack(
                fill="x", padx=12, pady=(0, 8)
            )


if __name__ == "__main__":
    app = CyberSentinelGUI()
    app.mainloop()
