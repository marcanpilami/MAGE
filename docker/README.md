# MAGE image Docker

Ceci est une image officielle pour MAGE (Module d'Assistance à la Gestion d'Environnement). L'image Docker fonctionne sur Linux, disponible sous licence Apache Public Licence, v2.


## 1. Qu'est ce que MAGE

MAGE est un outil d'assistance à la gestion d'environnement.

Il permet de centraliser l'ensemble de informations relative aux environnements d'un projet informatique: réalisation, publication.
Cette boite a outil du référentiel d'environnement a été conçu pour apporter un accès simplifié aux informations de connexion et de version au public, et assurer le suivi en version de la configuration.

La description complète du produit et sa documentation sont disponibles au lien suivant [read the docs](https://mage.readthedocs.io), le code est sur [GitHub](https://github.com/marcanpilami/MAGE).

## 2. Tags

Voici comment sont organisés les différents tag associés aux images docker:

* nightly : dernière image docker produite sur la base de la branche master, sans aucun support. Elle est mise est jour à chaque changement sur la branche master
* tag spécifique de release : chaque release a son propre tag représentant la version dans laquelle elle se trouve. Par exemple: 0.9.1    

## 3. Cas d'utilisation principaux

### 3.1 Réaliser un simple test

Lancement: `docker run -it --rm -e "DJANGO_ROOT_INITIAL_PASSWORD=something" -e "MAGE_CREATE_DEMO_DATA=True" -e "MAGE_ALLOW_MIGRATIONS=True" -port 8000:8000 enioka/mage`

Au lancement le serveur de l'application web démarre après quelques secondes. 
Un super utilisateur nommé `root` de mot de passe `something` est créé au lancement.

L'application est disponible en local sur la machine sur le port 8000 (exemple: accès navigateur http://localhost:8000)  

Utiliser la commande CTRL+C pour quitter. Toute modification sur le serveur sera perdue après interruption.


## 4. Image référence

* Variables d'environnement
  * Base de données
    * DATABASE_ENGINE: ou bien rien (ce qui correspond à une base sqlite3 locale dans un volume Docker) ou driver spécifique (`django.db.backends.postgresql_psycopg2` pour postresql, `django.db.backends.mysql` pour MySQL).
    * DATABASE_NAME: nom de la base de données
    * DATABASE_HOST: hôte (ou IP) du serveur portant la base de données
    * DATABASE_PORT: port de connexion à la base de données
    * DATABASE_USER: utilisateur se connectant à la base de données
    * DATABASE_PASSWORD: mot de passe associé à l'utilisateur
  * Propriétés de sécurité :
    * DJANGO_ALLOWED_HOSTS: MAGE filtre les requêtes HTTP ne provenant pas de ces hostnames. Liste séparée par des virgules. Wilcard * possible
    * DJANGO_SECRET_KEY: y mettre une chaine de caractère aléatoire. Utilisé pour certains chiffrements
    * DJANGO_ROOT_INITIAL_PASSWORD: si non vide, un compte applicatif nommé `root` est créé au démarrage avec ce mot de passe s'il n'existe pas déjà
  * Divers:
    * DJANGO_DEBUG: Activer l'affichage des informations de debug de l'application
    * MAGE_ALLOW_MIGRATIONS: autoriser la réalisation d'une migration de base de données (Django) dans le cas où cela est nécessaire
* Points de montage
  * /code/deployment/media: dossier partagé entre l'hôte et le conteneur Docker contenant les fichiers uploadés dans MAGE
  * /code/deployment/db: si vous utilisez sqlite, c'est le répertoire contenant le fichier de la base de données.
* Ports
  * 8000: Accès au service web et à son interface

## 5. FAQ
