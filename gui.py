import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from Virus_project import  load_signatures, scan_directory, quarantine_file, save_report

def escolher_pasta():
    pasta = filedialog.askdirectory(title="Escolhe a pasta para escanear")
    if pasta:
        entrada_pasta.set(pasta)

def correr_scan():
    pasta = entrada_pasta.get()
    if not pasta:
        messagebox.showwarning("Aviso", "Escolhe uma pasta primeiro!")
        return

    target_dir = Path(pasta)
    signatures = load_signatures(Path("signatures.json"))
    results = scan_directory(target_dir, signatures)

    infected = [r for r in results if r.status == "infected"]
    clean = [r for r in results if r.status == "clean"]

    resultado = f"Ficheiros limpos: {len(clean)}\nFicheiros infectados: {len(infected)}\n\n"
    for item in infected:
        resultado += f"[INFECTADO] {item.file_path}\n→ {item.reason}\n\n"

    texto_resultado.config(state="normal")
    texto_resultado.delete(1.0, tk.END)
    texto_resultado.insert(tk.END, resultado)
    texto_resultado.config(state="disabled")

    save_report(results, Path("output/scan_report.json"))
    label_status.config(text=f"Scan concluído — {len(infected)} infectado(s) encontrado(s)")

# JANELA PRINCIPAL
janela = tk.Tk()
janela.title("Scanner Antivírus")
janela.geometry("600x500")
janela.configure(bg="#0d140d")

# TÍTULO
tk.Label(janela, text="Scanner Antivírus", font=("Courier", 18, "bold"),
         bg="#0d140d", fg="#00ff88").pack(pady=20)

# ESCOLHER PASTA
entrada_pasta = tk.StringVar()
frame_pasta = tk.Frame(janela, bg="#0d140d")
frame_pasta.pack(pady=10, padx=20, fill="x")

tk.Entry(frame_pasta, textvariable=entrada_pasta, font=("Courier", 10),
         bg="#1a2e1a", fg="#e8f5e8", insertbackground="white",
         relief="flat", bd=5).pack(side="left", fill="x", expand=True)

tk.Button(frame_pasta, text="Escolher Pasta", command=escolher_pasta,
          bg="#00ff88", fg="#060a06", font=("Courier", 10, "bold"),
          relief="flat", padx=10).pack(side="right", padx=(10,0))

# BOTÃO SCAN
tk.Button(janela, text="INICIAR SCAN", command=correr_scan,
          bg="#00ff88", fg="#060a06", font=("Courier", 14, "bold"),
          relief="flat", padx=20, pady=10).pack(pady=20)

# ÁREA DE RESULTADOS
texto_resultado = tk.Text(janela, font=("Courier", 10),
                          bg="#060a06", fg="#00ff88",
                          relief="flat", bd=10, state="disabled")
texto_resultado.pack(padx=20, fill="both", expand=True)

# STATUS EM BAIXO
label_status = tk.Label(janela, text="Pronto para scan",
                         font=("Courier", 9), bg="#0d140d", fg="#5a7a5a")
label_status.pack(pady=10)

janela.mainloop()
