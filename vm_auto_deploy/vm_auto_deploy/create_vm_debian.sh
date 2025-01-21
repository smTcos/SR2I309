#!/bin/bash

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <VM_ID> <IP_ADDRESS> <USERNAME> <PASSWORD>"
  exit 1
fi


VM_ID=$1
IP=$2
USERNAME=$3
PASSWORD=$4
TEMPLATE_ID=9000 # Template cree avec le .qcow2 de debian, il possede lid 9000 dans notre env Proxmox
VM_NAME="debian-vm-$VM_ID"
GATEWAY="192.168.1.1"
DNS="8.8.8.8"
CIDR="/24"

# Verif si le modele existe
if ! qm status $TEMPLATE_ID >/dev/null 2>&1; then
  echo "Erreur : Le modèle avec ID $TEMPLATE_ID n'existe pas."
  exit 1
fi

# Verif de ne pas overwrite une autre VM avec le meme ID
if qm status $VM_ID >/dev/null 2>&1; then
  echo "Erreur : Une VM avec l'ID $VM_ID existe déjà."
  exit 1
fi

# Generer le mot de passe hashé pour Cloud-Init (SHA-512)
HASHED_PASSWORD=$(echo "$PASSWORD" | mkpasswd --method=SHA-512 --stdin)

# Creer le fichier reseau Cloud-Init pour cette VM
NETWORK_CONFIG_FILE="/var/lib/vz/snippets/network-config-$VM_ID.yaml"
cat <<EOF > $NETWORK_CONFIG_FILE
version: 2
ethernets:
  eth0:
    dhcp4: false
    addresses:
      - ${IP}${CIDR}
    gateway4: ${GATEWAY}
    nameservers:
      addresses:
        - ${DNS}
EOF

# Creation  dun fichier user-data Cloud-Init avec le suername et mdp
USER_DATA_FILE="/var/lib/vz/snippets/user-data-$VM_ID.yaml"
cat <<EOF > $USER_DATA_FILE
#cloud-config
locale: fr_FR.UTF-8
keyboard:
  layout: fr
timezone: Europe/Paris

users:
  - name: ${USERNAME}
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
    passwd: ${HASHED_PASSWORD}

  - name: root
    lock_passwd: false
    passwd: ${HASHED_PASSWORD}

package_update: true
packages:
  - sudo
  - vim
  - curl
  - wget

write_files:
  - path: /etc/ssh/sshd_config
    content: |
      PermitRootLogin yes
      PasswordAuthentication yes
      ChallengeResponseAuthentication no

runcmd:
  - sed -i 's/^PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
  - sed -i '/^PasswordAuthentication no/d' /etc/ssh/sshd_config
  - grep -qxF 'PasswordAuthentication yes' /etc/ssh/sshd_config || echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
  - systemctl restart sshd

EOF

# Cloner le modele 9000
qm clone $TEMPLATE_ID $VM_ID --name $VM_NAME

# Configuration Cloud-Init
qm set $VM_ID --ciuser $USERNAME --cipassword $PASSWORD
qm set $VM_ID --cicustom "user=local:snippets/user-data-$VM_ID.yaml,network=local:snippets/network-config-$VM_ID.yaml"

# Demarrage de la VM
echo "Démarrage de la VM..."
qm start $VM_ID


echo "VM $VM_NAME avec l'ID $VM_ID et IP $IP déployée avec succès !"
echo "Utilisateur : $USERNAME"
echo "Mot de passe root activé pour SSH."