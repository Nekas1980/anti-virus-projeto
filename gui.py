import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
import os
from Virus_project import load_signatures, load_exclusions, scan_file, quarantine_file, save_report, should_skip_path

# ─── CONFIGURAÇÃO VISUAL 2026 ──────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

MINT      = "#00ffa3"
CRIMSON   = "#ff0055"
BG_DARK   = "#030503"
SURFACE   = "#0d140d"
TEXT_MAIN = "#e8f5e8"
MUTED     = "#8fa88f"

# ─── CLASSE PRINCIPAL ────────────────────────────────
class CyberSentinelGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CYBER-SENTINEL // PROJETO ANTIVÍRUS 2026")
        self.geometry("1000x720")
        self.configure(fg_color=BG_DARK)

        # Variáveis de Estado
        self.pasta_alvo = ctk.StringVar()
        self.total_ficheiros = 0
        self.infectados = 0
        self.limpos = 0
        self.ignorados = 0
        self.results = []

        self.setup_ui()

    def setup_ui(self):
        # GRID CONFIG
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ─── SIDEBAR ──────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="// CYBER-SENTINEL", 
                                      font=ctk.CTkFont(family="Courier", size=18, weight="bold"),
                                      text_color=MINT)
        self.logo_label.pack(pady=(30, 40), padx=20)

        # Ações Rápidas
        self.btn_scan_pasta = self.create_sidebar_button("SCAN PASTA", self.correr_scan)
        self.btn_scan_rapido = self.create_sidebar_button("SCAN RÁPIDO", self.correr_scan_rapido)
        self.btn_scan_pc = self.create_sidebar_button("SCAN PC COMPLETO", self.correr_scan_pc)
        
        # Estatísticas (Bento Cards na Sidebar)
        self.stats_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=20, pady=20)
        
        self.lbl_stat_total = self.create_stat_widget(self.stats_frame, "TOTAL", TEXT_MAIN)
        self.lbl_stat_limpos = self.create_stat_widget(self.stats_frame, "LIMPOS", MINT)
        self.lbl_stat_infectados = self.create_stat_widget(self.stats_frame, "AMEAÇAS", CRIMSON)

        # ─── ÁREA CENTRAL ─────────────────────────────
        self.main_area = ctk.CTkFrame(self, corner_radius=24, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Header da Área Central
        self.header_frame = ctk.CTkFrame(self.main_area, fg_color=SURFACE, corner_radius=16, height=80)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_propagate(False)
        
        self.entry_pasta = ctk.CTkEntry(self.header_frame, textvariable=self.pasta_alvo, 
                                        placeholder_text="Selecione o diretório para análise...",
                                        width=500, height=40, border_color=MINT, fg_color=BG_DARK)
        self.entry_pasta.pack(side="left", padx=20, pady=20)
        
        self.btn_browse = ctk.CTkButton(self.header_frame, text="BROWSE", width=100, 
                                        command=self.escolher_pasta, fg_color=MINT, text_color=BG_DARK,
                                        hover_color=TEXT_MAIN, font=ctk.CTkFont(weight="bold"))
        self.btn_browse.pack(side="left", padx=(0, 20))

        # Log e Progresso
        self.content_frame = ctk.CTkFrame(self.main_area, fg_color=SURFACE, corner_radius=20)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        
        self.progress_bar = ctk.CTkProgressBar(self.content_frame, progress_color=MINT, height=12)
        self.progress_bar.pack(fill="x", padx=30, pady=(30, 10))
        self.progress_bar.set(0)
        
        self.lbl_status = ctk.CTkLabel(self.content_frame, text="PRONTO PARA SCAN", font=ctk.CTkFont(size=12), text_color=MUTED)
        self.lbl_status.pack(anchor="w", padx=30, pady=(0, 20))

        self.log_text = ctk.CTkTextbox(self.content_frame, fg_color=BG_DARK, text_color=MINT, 
                                       font=ctk.CTkFont(family="Courier", size=13), corner_radius=12)
        self.log_text.pack(fill="both", expand=True, padx=30, pady=(0, 30))

    # ─── MÉTODOS AUXILIARES UI ────────────────────────
    def create_sidebar_button(self, text, command):
        btn = ctk.CTkButton(self.sidebar, text=text, command=command, 
                           height=45, corner_radius=8, font=ctk.CTkFont(weight="bold"),
                           fg_color="transparent", border_width=1, border_color=MINT,
                           text_color=MINT, hover_color="rgba(0, 255, 163, 0.1)")
        btn.pack(fill="x", padx=20, pady=5)
        return btn

    def create_stat_widget(self, parent, label, color):
        frame = ctk.CTkFrame(parent, fg_color=BG_DARK, corner_radius=12, height=70)
        frame.pack(fill="x", pady=5)
        frame.pack_propagate(False)
        
        lbl_title = ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=10), text_color=MUTED)
        lbl_title.pack(pady=(8, 0), padx=15, anchor="w")
        
        lbl_val = ctk.CTkLabel(frame, text="0", font=ctk.CTkFont(size=24, weight="bold"), text_color=color)
        lbl_val.pack(padx=15, anchor="w")
        return lbl_val

    # ─── LÓGICA DO SCANNER ────────────────────────────
    def escolher_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_alvo.set(pasta)

    def adicionar_log(self, texto, tipo="info"):
        self.log_text.insert("end", f"{texto}\n")
        self.log_text.see("end")

    def reset_interface(self):
        self.log_text.delete("1.0", "end")
        self.progress_bar.set(0)
        self.lbl_stat_total.configure(text="0")
        self.lbl_stat_limpos.configure(text="0")
        self.lbl_stat_infectados.configure(text="0")
        self.infectados = 0
        self.limpos = 0
        self.results = []

    def correr_scan(self):
        pasta = self.pasta_alvo.get()
        if not pasta:
            messagebox.showwarning("Aviso", "Selecione uma pasta primeiro!")
            return
        self.reset_interface()
        threading.Thread(target=self.fazer_scan_multiplas, args=([Path(pasta)],), daemon=True).start()

    def correr_scan_rapido(self):
        user = os.path.expanduser("~")
        pastas = [Path(user) / "Downloads", Path(user) / "Desktop", Path("C:/Windows/Temp")]
        pastas = [p for p in pastas if p.exists()]
        self.reset_interface()
        self.adicionar_log("// INICIANDO SCAN RÁPIDO PROTOCOL...")
        threading.Thread(target=self.fazer_scan_multiplas, args=(pastas,), daemon=True).start()

    def correr_scan_pc(self):
        user = os.path.expanduser("~")
        pastas = [Path(user) / d for d in ["Downloads", "Desktop", "Documents", "Pictures"]]
        pastas = [p for p in pastas if p.exists()]
        self.reset_interface()
        self.adicionar_log("// INICIANDO FULL SYSTEM SCAN PROTOCOL...")
        threading.Thread(target=self.fazer_scan_multiplas, args=(pastas,), daemon=True).start()

    def fazer_scan_multiplas(self, pastas):
        signatures = load_signatures(Path("signatures.json"))
        exclusions = load_exclusions(Path("exclusions.json"))
        
        todos = []
        for pasta in pastas:
            for p in pasta.rglob("*"):
                if p.is_file() and not should_skip_path(p, exclusions):
                    todos.append(p)
        
        total = len(todos)
        if total == 0:
            self.adicionar_log("!! NENHUM FICHEIRO ENCONTRADO.")
            return

        self.lbl_stat_total.configure(text=str(total))
        self.adicionar_log(f"// ANALISANDO {total} FICHEIROS...\n")

        for i, ficheiro in enumerate(todos, 1):
            result = scan_file(ficheiro, signatures)
            self.results.append(result)
            
            progresso = i / total
            self.progress_bar.set(progresso)
            self.lbl_status.configure(text=f"ANALISANDO: {i} / {total} ({int(progresso*100)}%)")

            if result.status == "infected":
                self.infectados += 1
                self.lbl_stat_infectados.configure(text=str(self.infectados))
                self.adicionar_log(f"[!] AMEAÇA DETETADA: {result.file_path}")
                self.adicionar_log(f"    └─ TIPO: {result.reason}\n")
            else:
                self.limpos += 1
                self.lbl_stat_limpos.configure(text=str(self.limpos))

        save_report(self.results, Path("output/scan_report.json"))
        self.adicionar_log("──────────────────────────────────────────────────")
        self.adicionar_log("// SCAN CONCLUÍDO COM SUCESSO.")
        self.lbl_status.configure(text="SCAN CONCLUÍDO")

        if self.infectados > 0:
            if messagebox.askyesno("Ameaças Detetadas", f"Encontradas {self.infectados} ameaças. Isolar em quarentena?"):
                for r in self.results:
                    if r.status == "infected":
                        quarantine_file(Path(r.file_path), Path("quarantine"))
                self.adicionar_log("// PROTOCOLO DE QUARENTENA EXECUTADO.")

if __name__ == "__main__":
    app = CyberSentinelGUI()
    app.mainloop()
