import hashlib
import os

# Base de dados de exemplo (hashes de vírus conhecidos)
# Dica: Podes colocar aqui o hash MD5 do ficheiro de teste EICAR
MALWARE_DATABASE = {
    "44d88612fea8a8f36de82e1278abb02f": "EICAR-Test-File",
    "5e884898da28047151d0e56f8dc62927": "Exemplo-Malware-Falso"
}

def calcular_hash(caminho_ficheiro):
    """Calcula o MD5 de um ficheiro."""
    hash_md5 = hashlib.md5()
    try:
        with open(caminho_ficheiro, "rb") as f:
            # Lemos em blocos para não sobrecarregar a RAM com ficheiros grandes
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        print(f"Erro ao ler {caminho_ficheiro}: {e}")
        return None

def verificar_diretoria(caminho):
    """Percorre a pasta e verifica cada ficheiro."""
    print(f"--- A iniciar varredura em: {caminho} ---\n")
    
    for raiz, diretorias, ficheiros in os.walk(caminho):
        for nome in ficheiros:
            caminho_completo = os.path.join(raiz, nome)
            print(f"A analisar: {nome}...", end="\r")
            
            file_hash = calcular_hash(caminho_completo)
            
            if file_hash in MALWARE_DATABASE:
                print(f"\n[⚠️ ALERTA] Ameaça detetada: {MALWARE_DATABASE[file_hash]}")
                print(f"Caminho: {caminho_completo}\n")
            
    print("\n--- Varredura terminada ---")

if __name__ == "__main__":
    pasta_alvo = input("Introduza o caminho da pasta a analisar: ")
    if os.path.exists(pasta_alvo):
        verificar_diretoria(pasta_alvo)
    else:
        print("Caminho inválido.")