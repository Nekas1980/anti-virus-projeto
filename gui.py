import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
import os
from Virus_project import load_signatures, load_exclusions, scan_file, quarantine_file, save_report, should_skip_path

# ─── CORES ────────────────────────────────────────────
BG        = "#060a06"
SURFACE   = "#0d140d"
SURFACE2  = "#1a2e1a"
GREEN     = "#00ff88"
GREEN_DIM = "#00cc66"
RED       = "#ff4444"
BLUE      = "#00aaff"
AMBER     = "#ffaa00"
MUTED     = "#5a7a5a"
TEXT      = "#e8f5e8"

# ─── FUNÇÕES ──────────────────────────────────────────
def escolher_pasta():
    pasta = filedialog.askdirectory(title="Escolhe a pasta para escanear")
    if pasta:
        entrada_pasta.set(pasta)

def adicionar_log(texto, tipo="info"):
    cores = {
        "info":      BLUE,
        "limpo":     GREEN,
        "infectado": RED,
        "aviso":     AMBER,
        "muted":     MUTED,
    }
    texto_log.config(state="normal")
    texto_log.insert(tk.END, texto, tipo)
    texto_log.tag_config(tipo, foreground=cores.get(tipo, TEXT))
    texto_log.see(tk.END)
    texto_log.config(state="disabled")

def desenhar_grafico(limpos, infectados, ignorados):
    canvas.delete("all")
    total = limpos + infectados + ignorados
    if total == 0:
        return
    w, h = 220, 20
    canvas.create_rectangle(0, 0, w, h, fill=SURFACE2, outline="")
    x_limpo = int((limpos / total) * w)
    if x_limpo > 0:
        canvas.create_rectangle(0, 0, x_limpo, h, fill=GREEN, outline="")
    x_inf = int((infectados / total) * w)
    if x_inf > 0:
        canvas.create_rectangle(x_limpo, 0, x_limpo + x_inf, h, fill=RED, outline="")
    canvas.create_text(5, h + 15, anchor="w",
                       text=f"Limpos {limpos}", fill=GREEN, font=("Courier", 8))
    canvas.create_text(120, h + 15, anchor="w",
                       text=f"Infectados {infectados}", fill=RED, font=("Courier", 8))

def bloquear_botoes():
    btn_scan.config(state="disabled")
    btn_rapido.config(state="disabled")
    btn_pc.config(state="disabled")

def desbloquear_botoes():
    btn_scan.config(state="normal")
    btn_rapido.config(state="normal")
    btn_pc.config(state="normal")

def reset_interface():
    barra_progresso.config(value=0)
    texto_log.config(state="normal")
    texto_log.delete(1.0, tk.END)
    texto_log.config(state="disabled")
    lbl_total.config(text="0")
    lbl_limpos.config(text="0")
    lbl_infectados.config(text="0")
    lbl_ignorados.config(text="0")

def correr_scan():
    pasta = entrada_pasta.get()
    if not pasta:
        messagebox.showwarning("Aviso", "Escolhe uma pasta primeiro!")
        return
    bloquear_botoes()
    reset_interface()
    threading.Thread(target=fazer_scan_multiplas,
                     args=([Path(pasta)],), daemon=True).start()

def correr_scan_rapido():
    user = os.path.expanduser("~")
    pastas_risco = [
        Path(user) / "Downloads",
        Path(user) / "Desktop",
        Path(user) / "AppData" / "Local" / "Temp",
        Path("C:/Windows/Temp"),
    ]
    pastas = [p for p in pastas_risco if p.exists()]
    bloquear_botoes()
    reset_interface()
    adicionar_log("SCAN RÁPIDO — Pastas de risco:\n", "aviso")
    for p in pastas:
        adicionar_log(f"  → {p}\n", "muted")
    adicionar_log("\n", "muted")
    threading.Thread(target=fazer_scan_multiplas, args=(pastas,), daemon=True).start()

def correr_scan_pc():
    user = os.path.expanduser("~")
    pastas_pc = [
        Path(user) / "Downloads",
        Path(user) / "Desktop",
        Path(user) / "Documents",
        Path(user) / "AppData" / "Local" / "Temp",
        Path("C:/Windows/Temp"),
        Path(user) / "AppData" / "Roaming",
    ]
    pastas = [p for p in pastas_pc if p.exists()]
    bloquear_botoes()
    reset_interface()
    adicionar_log("SCAN PC COMPLETO — A analisar:\n", "infectado")
    for p in pastas:
        adicionar_log(f"  → {p}\n", "muted")
    adicionar_log("\n", "muted")
    threading.Thread(target=fazer_scan_multiplas, args=(pastas,), daemon=True).start()

def fazer_scan_multiplas(pastas):
    signatures = load_signatures(Path("signatures.json"))
    exclusions = load_exclusions(Path("exclusions.json"))
    todos = []
    for pasta in pastas:
        for p in pasta.rglob("*"):
            if p.is_file() and not should_skip_path(p, exclusions):
                todos.append(p)
    total = len(todos)

    if total == 0:
        adicionar_log("Nenhum ficheiro encontrado.\n", "aviso")
        desbloquear_botoes()
        return

    adicionar_log(f"Total de ficheiros a analisar: {total}\n\n", "info")
    lbl_total.config(text=str(total))

    results = []
    infectados = 0
    limpos = 0
    ignorados = 0

    for i, ficheiro in enumerate(todos, 1):
        result = scan_file(ficheiro, signatures)
        results.append(result)

        progresso = (i / total) * 100
        barra_progresso.config(value=progresso)
        lbl_progresso.config(text=f"{i} / {total}  ({int(progresso)}%)")

        if result.status == "infected":
            infectados += 1
            lbl_infectados.config(text=str(infectados))
            adicionar_log(f"[INFECTADO] {result.file_path}\n", "infectado")
            adicionar_log(f"          → {result.reason}\n\n", "infectado")
        elif result.status == "clean":
            limpos += 1
            lbl_limpos.config(text=str(limpos))
        else:
            ignorados += 1
            lbl_ignorados.config(text=str(ignorados))

        janela.update_idletasks()

    save_report(results, Path("output/scan_report.json"))
    desenhar_grafico(limpos, infectados, ignorados)

    adicionar_log(f"\n{'─'*55}\n", "muted")
    adicionar_log(f"  SCAN CONCLUÍDO\n", "info")
    adicionar_log(f"  Analisados : {total}\n", "info")
    adicionar_log(f"  Limpos     : {limpos}\n", "limpo")
    adicionar_log(f"  Infectados : {infectados}\n", "infectado" if infectados > 0 else "info")
    adicionar_log(f"  Relatório  : output/scan_report.json\n", "muted")
    adicionar_log(f"{'─'*55}\n", "muted")

    lbl_progresso.config(text="Scan concluído!")
    desbloquear_botoes()

    if infectados > 0:
        resposta = messagebox.askyesno("Infectados encontrados",
            f"Foram encontrados {infectados} ficheiro(s).\nMover para quarentena?")
        if resposta:
            for r in results:
                if r.status == "infected":
                    quarantine_file(Path(r.file_path), Path("quarantine"))
            adicionar_log("\n  Quarentena concluída.\n", "aviso")

# ─── JANELA ───────────────────────────────────────────
janela = tk.Tk()
janela.title("Scanner Antivírus v3")
janela.geometry("820x680")
janela.configure(bg=BG)
janela.resizable(True, True)

# ─── HEADER ───────────────────────────────────────────
header = tk.Frame(janela, bg=SURFACE, pady=12)
header.pack(fill="x")
tk.Label(header, text="// SCANNER ANTIVÍRUS", font=("Courier", 16, "bold"),
         bg=SURFACE, fg=GREEN).pack(side="left", padx=20)
tk.Label(header, text="v1.0 — Python", font=("Courier", 9),
         bg=SURFACE, fg=MUTED).pack(side="right", padx=20)

# ─── CORPO ────────────────────────────────────────────
corpo = tk.Frame(janela, bg=BG)
corpo.pack(fill="both", expand=True, padx=16, pady=12)

# ─── COLUNA ESQUERDA ──────────────────────────────────
col_esq = tk.Frame(corpo, bg=BG, width=240)
col_esq.pack(side="left", fill="y", padx=(0, 12))
col_esq.pack_propagate(False)

tk.Label(col_esq, text="DIRETÓRIO", font=("Courier", 8),
         bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 4))

entrada_pasta = tk.StringVar()
frame_entrada = tk.Frame(col_esq, bg=SURFACE2, pady=6, padx=8)
frame_entrada.pack(fill="x")
tk.Entry(frame_entrada, textvariable=entrada_pasta, font=("Courier", 9),
         bg=SURFACE2, fg=TEXT, insertbackground=GREEN,
         relief="flat", bd=0).pack(fill="x")

tk.Button(col_esq, text="Escolher Pasta", command=escolher_pasta,
          bg=SURFACE2, fg=GREEN, font=("Courier", 9),
          relief="flat", pady=6, cursor="hand2").pack(fill="x", pady=(4, 12))

# ─── BOTÕES ───────────────────────────────────────────
btn_scan = tk.Button(col_esq, text="SCAN PASTA", command=correr_scan,
                     bg=GREEN, fg=BG, font=("Courier", 11, "bold"),
                     relief="flat", pady=8, cursor="hand2")
btn_scan.pack(fill="x", pady=(0, 4))

btn_rapido = tk.Button(col_esq, text="SCAN RÁPIDO", command=correr_scan_rapido,
                       bg=AMBER, fg=BG, font=("Courier", 11, "bold"),
                       relief="flat", pady=8, cursor="hand2")
btn_rapido.pack(fill="x", pady=(0, 4))

btn_pc = tk.Button(col_esq, text="SCAN PC COMPLETO", command=correr_scan_pc,
                   bg=RED, fg=TEXT, font=("Courier", 11, "bold"),
                   relief="flat", pady=8, cursor="hand2")
btn_pc.pack(fill="x", pady=(0, 16))

tk.Frame(col_esq, bg=SURFACE2, height=1).pack(fill="x", pady=8)

# ─── ESTATÍSTICAS ─────────────────────────────────────
tk.Label(col_esq, text="ESTATÍSTICAS", font=("Courier", 8),
         bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 8))

def stat_card(parent, label, cor):
    f = tk.Frame(parent, bg=SURFACE, pady=10, padx=12)
    f.pack(fill="x", pady=3)
    tk.Label(f, text=label, font=("Courier", 8), bg=SURFACE, fg=MUTED).pack(anchor="w")
    lbl = tk.Label(f, text="0", font=("Courier", 20, "bold"), bg=SURFACE, fg=cor)
    lbl.pack(anchor="w")
    return lbl

lbl_total      = stat_card(col_esq, "TOTAL",      TEXT)
lbl_limpos     = stat_card(col_esq, "LIMPOS",     GREEN)
lbl_infectados = stat_card(col_esq, "INFECTADOS", RED)
lbl_ignorados  = stat_card(col_esq, "IGNORADOS",  MUTED)

tk.Frame(col_esq, bg=SURFACE2, height=1).pack(fill="x", pady=12)

tk.Label(col_esq, text="DISTRIBUIÇÃO", font=("Courier", 8),
         bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 6))
canvas = tk.Canvas(col_esq, bg=BG, height=50, width=220, highlightthickness=0)
canvas.pack(fill="x")

# ─── COLUNA DIREITA ───────────────────────────────────
col_dir = tk.Frame(corpo, bg=BG)
col_dir.pack(side="left", fill="both", expand=True)

tk.Label(col_dir, text="LOG EM TEMPO REAL", font=("Courier", 8),
         bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 4))

style = ttk.Style()
style.theme_use("default")
style.configure("g.Horizontal.TProgressbar",
                background=GREEN, troughcolor=SURFACE2,
                bordercolor=BG, lightcolor=GREEN, darkcolor=GREEN_DIM)

barra_progresso = ttk.Progressbar(col_dir, style="g.Horizontal.TProgressbar",
                                   orient="horizontal", mode="determinate")
barra_progresso.pack(fill="x", pady=(0, 4))

lbl_progresso = tk.Label(col_dir, text="Pronto para scan",
                          font=("Courier", 9), bg=BG, fg=MUTED)
lbl_progresso.pack(anchor="w", pady=(0, 8))

frame_log = tk.Frame(col_dir, bg=SURFACE)
frame_log.pack(fill="both", expand=True)

scroll = tk.Scrollbar(frame_log)
scroll.pack(side="right", fill="y")

texto_log = tk.Text(frame_log, font=("Courier", 9),
                    bg=SURFACE, fg=GREEN,
                    relief="flat", bd=10, state="disabled",
                    yscrollcommand=scroll.set)
texto_log.pack(fill="both", expand=True)
scroll.config(command=texto_log.yview)

# ─── FOOTER ───────────────────────────────────────────
footer = tk.Frame(janela, bg=SURFACE, pady=6)
footer.pack(fill="x", side="bottom")
tk.Label(footer, text="Projeto Antivírus — IEFP 2026 | github.com/Nekas1980",
         font=("Courier", 8), bg=SURFACE, fg=MUTED).pack()

janela.mainloop()