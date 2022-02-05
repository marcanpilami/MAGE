MAGE - Module d'Assistance à la Gestion d'Environnement
============================================================

(in French - MAGE is not localized in other languages yet)

MAGE est un framework permettant de facilement mettre en place un outillage de gestion d'environnements sur un projet informatique. 

Il est principalement destiné aux projets qui ont de multiples environnements, dont la gestion peut vite devenir complexe. Il fournit autant les fonctions indispensables à la réalisation des outils (téléchargement des packages d'installation, suivi en version, ...) que la partie "publication" pouvant drastiquement diminuer la charge de communication des administrateurs, avec notamment un portail donnant toutes les informations de connexion et de version au public.

Ce framework couvre donc les aspects suivants :

* Référentiel des environnements
	* Stockage des descriptions (machines, logins, ...), que l'on peut saisir ou modifier à l'aide d'un site web ergonomique
    * Gestion fine des normes de nommage pour faciliter la création des composants et le respect des normes
	* API d'interrogation web (en général de simples GET) pour les scripts (qui par exemple iront chercher une chaîne de connexion dans le référentiel)
	* Publication du référentiel sur un portail (avec plusieurs niveaux de sécurité intégrés)
    * Outil très paramétrable de cartographie des environnements 
    * Puissant langage de requête
    * Possibilités d'export JSON, CSV (Excel) et sous forme de scripts shell
* Gestion de configuration Logicielle (GCL)
	* Référencement des packages et sauvegardes, avec gestion des dépendances en version
    * DSL: centralisation de la gestion des livraisons, qui deviennent facilement accessibles en HTTP. La DSL est doté d'un workflow de validation simple
    * Vérification automatique du format et contenu des packages
	* Référencement des installations et restaurations, permettant un suivi précis de la configuration des composants au fil du temps. (également via HTTP pour faciliter l'intégration avec des scripts shell)
    * Nombreuses API web permettant à un script de tester si un environnement respecte les pré requis d'installation d'un package, si une sauvegarde est en cours, ...
	* Publication des versions courantes et passées sur le portail
    * Gestion d'ensembles de version de référence ("tags")
* Transverse
    * Gestion simple des habilitations, avec de base seulement trois rôles clairs (toute cette gestion pouvant être finement adaptée à tous les besoins si nécessaire)
    * L'authentification peut être déléguée à un serveur LDAP
