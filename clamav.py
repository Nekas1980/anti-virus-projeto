import json

print("Olá, scanner ClamAV pronto para uso")

config = {
    "name": "ClamAV",
    "version": "0.2.0"
}

print(json.dumps(config, indent=2))