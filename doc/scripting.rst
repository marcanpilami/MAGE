##############################################
Réaliser des scripts autours de MAGE (A FINIR)
##############################################

MAGE, grâce à son référentiel, devient le coeur de l'exploitation des
environnements.
Cependant, très souvent, les scripts d'exploitation (sauvegarde, 
application de patch...) seront réalisés dans un langage qui n'est pas
Python.

Ce document décrit donc différents moyen souples et aisés d'interfacer
des scripts de n'importe quel language avec MAGE.


***********************
Interface référentiel
***********************

Pour interfacer des scripts non Python, MAGE propose une interface 
d’interrogation du référentiel basique rendant un csv contenant tous 
les champs d’un ou plusieurs composants.

Pour identifier un composant, MAGE a adopté une notation claire, souple
et pratique (si !). On désigne un composant tout d’abord par son nom 
d’instance OU son nom de classe, puis, si cela ne suffit pas, on indique
le nom d’instance OU le nom de classe d’un de ses parents, puis on 
continue ainsi jusqu’à ce qu’on trouve.
Il suffit de donner le minimum d’informations. S’il n’y a qu’un seul 
composant d’un nom d’instance donné, il suffit de donner son nom. De 
plus, MAGE considère toujours l’ensemble des informations qu’on lui 
soumet. Il est donc inutile, voir risqué, de donner trop  d’information !

Dans le cas de notre application, les scripts de GE auront besoin le plus souvent de se connecter à un schéma. Un schéma est identifié de façon unique par son nom d’instance et le nom d’instance de l’instance Oracle, donc en deux informations maximum on sera à même de retrouver toutes les informations du schéma. (et une seule information pour l’instance).

Pour retrouver « schéma1 » sur « Instance1 », (ainsi qu’"Instance1") on 
pourra au choix : ::

	python ask_ref.py –c"schéma1,Instance1” –c”Instance1”

ou bien interroger, via un utilitaire comme wget, l’adresse suivante :
 `http://RACINE/MAGE/ref/csv/schéma1,Instance1/Instance1` 

Ce qui donnera le même résultat.

La ligne de commande permet de plus de filtrer par environnement (en 
précisant –eENVT_NAME), et d’afficher, pour chaque ligne retournée, 
la description de chaque champ.

Le référentiel est donc interrogeable quel que soit le type de 
déploiement retenu. (centralisé ou en déployant les scripts Python sur 
toutes les machines).
L’interrogation web est normalement plus rapide (aux aléas réseau près) 
vu que le server web garde en général des process Python ouverts, alors 
que le script doit lancer un nouveau process Python et charger 
Django+Mage.

Dans un avenir plus ou moins proche, des pages Mage seront protégées 
par un système d’authentification basique. Non encore défini, mais très 
probablement identification http de base pour rester compatible 
simplement avec wget.


***********************
Interface GCL (TODO)
***********************

***********************
Interface sav (TODO)
***********************

