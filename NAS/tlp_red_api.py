from flask import Flask, request, jsonify, send_file
import subprocess
import os

app = Flask(__name__)

# Fichiers pour la whitelist et les tokens
WHITELIST = "/mnt/private/whitelist_tlp_red.txt"
TOKENS_DIR = "/mnt/private/tokens"
TLP_RED_PATH = "/mnt/private/TLP_RED"

# Endpoint principal : acces au fichier
"""
Exemple dutilisation : 
curl -v -X POST http://10.0.0.1:5000/api/access_file \
    -H "Content-Type: application/json" \
    -d '{
        "user": "directeur",
        "password": "password_red",
        "file_path": "/data/TLP_RED1.txt",
        "token": "5f04298e0e29ff8dadb2b0ade3f6e69520913d58601ea74e479fd85c6bc99feb"
    }' \
    -O -J
"""


@app.route('/api/access_file', methods=['POST'])
def access_file():
    data = request.json
    user = data.get('user')
    password = data.get('password')
    file_path = data.get('file_path')
    token = data.get('token')

    #Verification de la whitelist
    if not user_in_whitelist(user):
        return jsonify({"status": "error", "message": "Utilisateur non autorisé"}), 403

    # Authentification SFTP
    if not authenticate_sftp(user, password):
        return jsonify({"status": "error", "message": "Échec de l'authentification SFTP"}), 401



    if not token:
        return jsonify({"status": "error", "message": "Jeton requis pour accéder à ce fichier"}), 403

    # Validation du jeton
    valid, message = validate_user_token(user, TLP_RED_PATH+file_path, token)
    if not valid:
        return jsonify({"status": "error", "message": message}), 403

    # Livraison du fichier
    if not os.path.exists(TLP_RED_PATH+file_path):
        return jsonify({"status": "error", "message": "Fichier introuvable"}), 404

    #return send_file(TLP_RED_PATH+file_path, as_attachment=True)
    filename = os.path.basename(TLP_RED_PATH+file_path)
    response = send_file(TLP_RED_PATH+file_path, as_attachment=True)
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    print(f"Content-Disposition: {response.headers['Content-Disposition']}")
    return response

#Endpoint secondaire : consultation arborescence fichiers TLP_RED
"""
Exemple dutilisation : 
curl -v -X POST http://10.0.0.1:5000/api/tlp_red_tree \
    -H "Content-Type: application/json" \
-d '{
    "user": "directeur",
    "password": "password_red"}'

"""
@app.route('/api/tlp_red_tree', methods=['POST'])
def tlp_red_tree():
    data = request.json
    user = data.get('user')
    password = data.get('password')

    #Verification de la whitelist
    if not user_in_whitelist(user):
        return jsonify({"status": "error", "message": "Utilisateur non autorisé"}), 403

    # Authentification SFTP
    if not authenticate_sftp(user, password):
        return jsonify({"status": "error", "message": "Échec de l'authentification SFTP"}), 401

    # Parcourir larborescence
    file_tree = []
    for root, dirs, files in os.walk(TLP_RED_PATH):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), TLP_RED_PATH)
            file_tree.append(relative_path)

    return jsonify({"status": "success", "files": file_tree}), 200


# Fonction : Verification de la whitelist
def user_in_whitelist(user):
    with open(WHITELIST, 'r') as f:
        whitelist = f.read().splitlines()
    return user in whitelist

# Fonction : Authentification SFTP  
def authenticate_sftp(user, password):
    import paramiko

    try:
        # Connexion au serveur SFTP
        transport = paramiko.Transport(('127.0.0.1', 2223))  # Adapter si le serveur SFTP est ailleurs
        transport.connect(username=user, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Verification de lacces au repertoire TLP_RED
        sftp.listdir('/')
        sftp.close()
        return True
    except Exception as e:
        print(f"SFTP authentication failed: {e}")
        return False


# Fonction : Validation du jeton
def validate_user_token(user, file_path, provided_token):
    token_file = os.path.join(TOKENS_DIR, f"{user}_token.txt")
    if not os.path.exists(token_file):
        return False, "Aucun jeton trouvé pour l'utilisateur"

    with open(token_file, 'r') as f:
        stored_data = f.read().strip().split(":")
        stored_user, stored_file, stored_token, timestamp = stored_data

    if stored_user != user or stored_file != file_path:
        return False, "Jeton invalide pour cet utilisateur ou fichier"

    # Verifier la validite du jeton
    secret_key = "my_super_secret_key"
    expected_token = subprocess.getoutput(f"echo -n '{user}:{file_path}:{timestamp}:{secret_key}' | sha256sum | awk '{{print $1}}'")
    if expected_token != provided_token:
        return False, "Jeton incorrect"

    return True, "Jeton valide"

# Lancer l'API
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

