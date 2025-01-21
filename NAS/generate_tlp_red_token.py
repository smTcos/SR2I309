#!/usr/bin/env python3

import hashlib
import time
import os
import sys

# Configuration
#Repertoire contenant les tokens
TOKENS_DIR = "/mnt/private/tokens"

#A CHANGER EN PROD
#Cle secrete de ladministrateur
SECRET_KEY = "my_super_secret_key"

def generate_token(user, file_path):
    """Genere un jeton securise base sur lutilisateur, le chemin et une cle secrete."""
    timestamp = int(time.time())
    token_data = f"{user}:{file_path}:{timestamp}:{SECRET_KEY}" #Format du jeton unique detaille dans rapport
    token = hashlib.sha256(token_data.encode()).hexdigest() # Utilisation de sha256 sur la string concat
    return token, timestamp

def save_token(user, file_path, token, timestamp):
    """Enregistre le jeton genere dans un fichier utilisateur."""
    token_file = os.path.join(TOKENS_DIR, f"{user}_token.txt")
    with open(token_file, "w") as f:
        f.write(f"{user}:{file_path}:{token}:{timestamp}")
    print(f"Jeton sauvegarde dans {token_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: generate_tlp_red_token.py <user> <file_path>")
        sys.exit(1)

    user = sys.argv[1]
    file_path = sys.argv[2]

    #Verifier si le fichier existe
    if not os.path.exists(file_path):
        print(f"Erreur : Le fichier {file_path} n existe pas.")
        sys.exit(1)

    #Verifier si le dossier des jetons existe
    if not os.path.exists(TOKENS_DIR):
        os.makedirs(TOKENS_DIR)

    # Generation et sauvegarde du jeton
    token, timestamp = generate_token(user, file_path)
    save_token(user, file_path, token, timestamp)

    print(f"Jeton genere avec succes pour l utilisateur '{user}' et le fichier '{file_path}':")
    print(f"Token : {token}")
    print(f"Timestamp : {timestamp}")

if __name__ == "__main__":
    main()

