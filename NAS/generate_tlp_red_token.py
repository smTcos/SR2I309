#!/usr/bin/env python3

import hashlib
import time
import os
import sys

# Configuration
TOKENS_DIR = "/mnt/private/tokens"
SECRET_KEY = "my_super_secret_key"

def generate_token(user, file_path):
    """Génère un jeton sécurisé basé sur l'utilisateur, le chemin et une clé secrète."""
    timestamp = int(time.time())
    token_data = f"{user}:{file_path}:{timestamp}:{SECRET_KEY}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    return token, timestamp

def save_token(user, file_path, token, timestamp):
    """Enregistre le jeton généré dans un fichier utilisateur."""
    token_file = os.path.join(TOKENS_DIR, f"{user}_token.txt")
    with open(token_file, "w") as f:
        f.write(f"{user}:{file_path}:{token}:{timestamp}")
    print(f"Jeton sauvegardé dans {token_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: generate_tlp_red_token.py <user> <file_path>")
        sys.exit(1)

    user = sys.argv[1]
    file_path = sys.argv[2]

    # Vérifier si le fichier existe
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} n'existe pas.")
        sys.exit(1)

    # Vérifier si le dossier des jetons existe
    if not os.path.exists(TOKENS_DIR):
        os.makedirs(TOKENS_DIR)

    # Générer et sauvegarder le jeton
    token, timestamp = generate_token(user, file_path)
    save_token(user, file_path, token, timestamp)

    print(f"Jeton généré avec succès pour l'utilisateur '{user}' et le fichier '{file_path}':")
    print(f"Token : {token}")
    print(f"Timestamp : {timestamp}")

if __name__ == "__main__":
    main()

