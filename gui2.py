import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import threading
from Virus_project import load_signatures, scan_file, quarantine_file, save_report

def escolher_pasta():
    pasta = filedialog.askdirectory(title="Escolhe a pasta para escanear")
    if pasta:
        entrada_pasta.set(pasta)

def correr_scan():
    pasta = entrada_pasta.get()
    if not pasta:
        messagebox.showwarning("Aviso", "Escolhe uma pasta primeiro!")
        return

    # Desactiva botão durante o scan
    btn_scan.config(state="disabled")
    barra_progresso.config(value=0)
    texto_log.config(state="normal")
    texto_log.delete(1.0, tk.END)

    # Corre em thread separada para não bloquear a janela
    threading.Thread(target=fazer_scan, args=(pasta,), daemon=True).start()

def fazer_scan(pasta):
    target_dir = Path(pasta)
    signatures = load_signatures(Path("assinaturas.json"))

    # Conta total de ficheiros primeiro
    ficheiros = [p for p in target_dir.rglob("*") if p.is_file()]
    total = len(ficheiros)

    if total == 0:
        adicionar_log("Nenhum ficheiro encontrado.\n", "aviso")
        btn_scan.config(state="normal")
        return

    adicionar_log(f"A iniciar scan — {total} ficheiros encontrados\n", "info")

    results = []
    infectados = 0

    for i, ficheiro in enumerate(ficheiros, 1):
        result = scan_file(ficheiro, signatures)
        results.append(result)

        # Actualiza barra de progresso
        progresso = (i / total) * 100
        barra_progresso.config(value=progresso)
        label_progresso.config(text=f"{i}/{total} ficheiros analisados")

        # Log em tempo real
        if result.status == "infected":
            infectados += 1
            adicionar_log(f"[INFECTADO] {result.file_path}\n", "infectado")
            adicionar_log(f"           → {result.reason}\n", "infectado")
        else:
            adicionar_log(f"[LIMPO] {result.file_path}\n", "limpo")

        janela.update_idletasks()

    # Resultado final
    adicionar_log(f"\n{'='*50}\n", "info")
    adicionar_log(f"SCAN CONCLUÍDO\n", "info")
    adicionar_log(f"Ficheiros analisados: {total}\n", "info")
    adicionar_log(f"Ficheiros limpos: {total - infectados}\n", "limpo")
    adicionar_log(f"Ficheiros infectados: {infectados}\n", "infectado" if infectados > 0 else "info")

    save_report(results, Path("output/scan_report.json"))
    adicionar_log(f"Relatório guardado em output/scan_report.json\n", "info")

    btn_scan.config(state="normal")
    label_progresso.config(text="Scan concluído!")

def adicionar_log(texto, tipo="info"):
    cores = {
        "info":      "#00aaff",
        "limpo":     "#00ff88",
        "infectado": "#ff4444",
        "aviso":     "#ffaa00",
    }
    texto_log.config(state="normal")
    texto_log.insert(tk.END, texto, tipo)
    texto_log.tag_config(tipo, foreground=cores[tipo])
    texto_log.see(tk.END)
    texto_log.config(state="disabled")

# JANELA PRINCIPAL
janela = tk.Tk()
janela.title("Scanner Antivírus v2")
janela.geometry("700x600")
janela.configure(bg="#0d140d")
janela.resizable(True, True)

# TÍTULO
tk.Label(janela, text="Scanner Antivírus", font=("Courier", 18, "bold"),
         bg="#0d140d", fg="#00ff88").pack(pady=15)

# ESCOLHER PASTA
entrada_pasta = tk.StringVar()
frame_pasta = tk.Frame(janela, bg="#0d140d")
frame_pasta.pack(pady=5, padx=20, fill="x")

tk.Entry(frame_pasta, textvariable=entrada_pasta, font=("Courier", 10),
         bg="#1a2e1a", fg="#e8f5e8", insertbackground="white",
         relief="flat", bd=5).pack(side="left", fill="x", expand=True)

tk.Button(frame_pasta, text="Escolher Pasta", command=escolher_pasta,
          bg="#00ff88", fg="#060a06", font=("Courier", 10, "bold"),
          relief="flat", padx=10).pack(side="right", padx=(10,0))

# BARRA DE PROGRESSO
frame_prog = tk.Frame(janela, bg="#0d140d")
frame_prog.pack(pady=10, padx=20, fill="x")

style = ttk.Style()
style.theme_use("default")
style.configure("green.Horizontal.TProgressbar",
                background="#00ff88", troughcolor="#1a2e1a",
                bordercolor="#0d140d", lightcolor="#00ff88", darkcolor="#00cc66")

barra_progresso = ttk.Progressbar(frame_prog, style="green.Horizontal.TProgressbar",
                                   orient="horizontal", length=400, mode="determinate")
barra_progresso.pack(fill="x")

label_progresso = tk.Label(janela, text="Pronto para scan",
                            font=("Courier", 9), bg="#0d140d", fg="#5a7a5a")
label_progresso.pack()

# BOTÃO SCAN
btn_scan = tk.Button(janela, text="INICIAR SCAN", command=correr_scan,
                     bg="#00ff88", fg="#060a06", font=("Courier", 14, "bold"),
                     relief="flat", padx=20, pady=8)
btn_scan.pack(pady=10)

# LOG EM TEMPO REAL
tk.Label(janela, text="LOG EM TEMPO REAL", font=("Courier", 9),
         bg="#0d140d", fg="#5a7a5a").pack(anchor="w", padx=20)

frame_log = tk.Frame(janela, bg="#060a06", bd=2, relief="flat")
frame_log.pack(padx=20, pady=5, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame_log)
scrollbar.pack(side="right", fill="y")

texto_log = tk.Text(frame_log, font=("Courier", 9),
                    bg="#060a06", fg="#00ff88",
                    relief="flat", bd=5, state="disabled",
                    yscrollcommand=scrollbar.set)
texto_log.pack(fill="both", expand=True)
scrollbar.config(command=texto_log.yview)

janela.mainloop()