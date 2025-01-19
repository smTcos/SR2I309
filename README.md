# Projet Cloud Hybride : Architecture Sécurisée pour Données Sensibles

Ce projet implémente une solution hybride de gestion des données basée sur les niveaux de sensibilité définis par le **Traffic Light Protocol (TLP)**. Le dépôt inclut le code, les scripts de configuration, ainsi que les instructions nécessaires pour déployer et sécuriser les environnements public et privé.

## Contenu du Dépôt

- **NAS/** : Contient des données de tests classées TLP :AMBER et TLP :RED, ainsi que les scripts Python nécessaires à l'API de gestion des données TLP :RED.
- **[SR2I309] rapport-cloud.pdf** : Fichier complet et explicatif étapes par étapes.


## Fonctionnalités

1. **Segmentation des données choisie** :
   - **TLP :WHITE** : Données publiques (sorte de site vitrine) accessibles à toute personne de l'entreprise et les externes (journalistes par exemple) via Nextcloud.
   - **TLP :GREEN** : Données internes accessibles au personnel interne de l'entreprise.
   - **TLP :AMBER** : Données sensibles restreintes à des utilisateurs habilités dans un cloud privé.
   - **TLP :RED** : Données hautement sensibles avec des accès contrôlés par jetons.

2. **Connexion sécurisée** :
   - VPN WireGuard pour relier le cloud public et privé.
   - Pare-feu configuré avec iptables pour limiter les accès.

3. **Gestion des utilisateurs et des habilitations** :
   - Groupes et permissions définis pour chaque niveau TLP.
   - Systèmes de journalisation avancée via Nextcloud.

4. **Automatisation** :
   - Scripts pour le déploiement des VMs et des configurations. (non fourni ici)

## Installation

### Pré-requis

- Un serveur de virtualisation (Proxmox ou équivalent).
- Accès à un environnement Debian sans interface graphique.
- Droits administratifs sur les machines pour exécuter les scripts fournis.

### Les grandes étapes

1. **Création des VMs** :
   Utilisez le script de déploiement automatique :
   ```bash
   ./create_vm_debian.sh <ID_VM> <IP> <USER> <PASSWORD>
   ```

2. **Configuration des environnements** :
   - Suivez les instructions dans `nextcloud_config/` pour configurer le cloud public.
   - Configurez les habilitations et dossiers pour les données sensibles dans `NAS/`.

3. **Connexion VPN** :
   Configurez WireGuard en suivant les fichiers de configuration fournis.

4. **Finalisation** :
   - Vérifiez les logs et assurez-vous que tous les services sont opérationnels.
   - Testez les accès utilisateur et ajustez les permissions si nécessaire.

## Utilisation

### Accès aux environnements

- **VM-Nextcloud (cloud public)** :
  Accès à l’interface web :
  ```
  URL : http://127.0.0.1:8080/nextcloud
  ```

- **VM-NAS (cloud privé)** :
  Accès SSH :
  ```bash
  ssh -J <PROXY_VM> <USER>@<IP_VM>
  ```

### Gestion des utilisateurs

Les commandes d’administration Nextcloud sont disponibles dans la section `scripts/`. Exemples :
- Ajouter un utilisateur :
  ```bash
  sudo -u www-data php occ user:add <NOM_UTILISATEUR>
  ```

## Notes de sécurité

- **Changement des mots de passe par défaut** : Obligatoire avant la mise en production.
- **Durcissement des configurations** : Activez l’authentification forte et limitez les accès réseau.
- **Journalisation** : Configurez un système de centralisation des logs pour surveiller les activités.

## Contributions

Les contributions au projet sont les bienvenues ! Veuillez soumettre vos pull requests ou signaler les problèmes via l’onglet Issues.

## Auteurs

- Lucas Maracine
- Loic Testa

## Licence

Ce projet est sous licence MIT.
