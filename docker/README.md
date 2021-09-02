# MAGE image Docker

Ceci est une image officielle pour MAGE (Module d'Assistance à la Gestion d'Environnement). L'image Docker fonctionne sur Linux, disponible sous licence Apache Public Licence, v2.


## 1. Qu'est ce que MAGE

MAGE est un outil d'assitance à la gestion d'environnement.

Il permet de centraliser l'ensemble de informations relative aux environements d'un projet informatique: réalisation, publication.
Cette boite a outil du référentiel d'environnement a été conçu pour apporter un accès simplifier aux informations de connexion et de versions au public. 

La description complète du produit et sa documentation est disponible au lien suivant [read the docs](https://mage.readthedocs.io), le code est sur [GitHub](https://github.com/marcanpilami/MAGE). Support (Marc-Antoine Gouillart company).
Cette application a été conçu à l'aide du framework Django.

## 2. Tags

Voici comment sont organisés les différents tag associés au images docker:

* nightly : dernière image docker produite sur la base de la branche master, sans auncun support. Elle est mise est jour à chaque changement sur la branche master
* tag spécifique de release : chaque release a son propre tag représentant la version dans laquel elle se trouve, exemple: 0.9.1    

## 3. Cas d'utilisation principaux

### 3.1 Réaliser un simple test

Lancement: `docker run -it --rm -port 8000:8000 enioka/mage`

Au lancement le serveur de l'application web démarre après quelques secondes. 
Un super utilisateur est créer au lancement. Pour cela, les informations suivantes vous seront demandés :
* Nom de l'utilisateur (optionel: 'apache' par défaut )
* Email (optionel)
* Mot de passe (et confirmation associée)
L'application est disponible en locale sur la machine sur le port 8000 (exemple: accès navigateur localhost:8000)  

Utiliser la commande CTRL+C pour quitter. Toute modification sur le serveur sera perdue après interruption.

### 3.2 Réaliser une DSL

Lancement: `docker run -it --rm -port 8000:8000 -v <chemin/acces/au/dossier/contenant/les/DSL>:/var/www/MAGE/tmp/media enioka/mage`

La nommination du chemin d'accès vers le dossier contenant la DSL permet de la rendre accessible à l'application et de réaliser le paramétrage désiré.

## 4. Image reference

* Variables d'environment
  * DATABASE_ENGINE: moteur de base de données (par défaut sqlite)
  * DATABASE_NAME: nom de la base de données
  * DATABASE_HOST: hôte avec lequel se connecter à la base de données
  * DATABASE_PORT: port de connexion à la base de di
  * DATABASE_USER: utilisateur se connectant à la base de données
  * DATABASE_PASSWORD: mot de passe associé à l'utilisatuer
  * ALLOWED_HOSTS: Liste de hôtes pour lesquelles l'application peut délivrer le contenu (exemple: www.example.com, tous par défaut) 
  * DEBUG: Activer l'affichage des informations de debug de l'application
  * INTERNAL_IPS
  * SECRET_KEY
  * AZURE_ACCOUNT_NAME
  * AZURE_ACCOUNT_KEY
  * AZURE_CONTAINER
  * MAGE_ALLOW_MIGRATIONS: autoriser la réalisation d'une migration de base de données (Django) dans le cas où cela est nécessaire
* Point de montage
  * /var/www/MAGE/tmp/media: dossier partagé entre l'hôte et le contenaire Docker contenant les DSL 
* Ports
  * 8000: Accès au service web et à son interface

## 5. FAQ
