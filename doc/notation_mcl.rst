###############################################
API recherche référentiel & Notation MCL
###############################################

.. module:: MAGE.ref.helpers
	:synopsis: API for finding components given minimal data
.. moduleauthor:: Marc-Antoine Gouillart 


\ *Mage Component Locator* (MCL) est la très pédante dénomination de la
notation permettant d'identifer facilement un composant de façon unique
dans le référentiel.

Cette notation est avant tout faite pour trouver un composant particulier, 
pas pour lister des composants. Cependant, vous verrez qu'en jouant
sur les noms de classe elle s'adapte facilement à ce second usage. 

Elle admet deux formes : une *notation simplifiée* et sa *forme complète*\ .
Dans les deux cas, elle repose sur la généalogie des composants, c'est à
dire qu'une composant sera identifié par son nom, puis le nom d'un de ses
pères, puis d'un père de ce père, etc.

La notation est décrite dans ce document telle qu'elle doit être utilisée
dans les appels de script, i.e. sous forme de chaîne de caractères. Nous décrirons
ensuite différentes fonctions qui permettent de l'utiliser avec des objets Python.


******************
Forme simplifiée
******************

------------
Syntaxe
------------

::

	nom[,nom_père[,nom_grand_pere[...]]][|nom_environnement][|nom_modele]

Attention, les "noms" sont ou bien les noms d'instance de composant, ou bien
leurs noms de classe (et les deux peuvent être mélangés dans la même désignation
de composant).

.. note:: Si certains éléments peuvent être omis, leur ordre est **obligatoire**\ .

------------
Résolution
------------

MAGE prendra tous les composants de ces noms (d'instance ou de classe), puis, 
pour chaque résultat, regardera s'il a un parent correspondant au nom donné.
Et ainsi de suite jusqu'à ce que tous les noms donnés aient été utilisés.

Conséquences importantes :

* Tous les noms donnés sont toujours utilisés. Donc si vous donnez trop d'informations
  et que ces informations en trop sont eronnées ou trop restrictives, vous n'aurez
  aucun résultat.
* MAGE n'analyse qu'une unique chaine de parenté. On ne peut chercher en donnant
  le nom du père, puis le nom du grand-père maternel par exemple. Il faut toujours
  remonter une unique branche de l'arbre généalogique.



***************
Forme complète
***************

La forme simple suffit la plupart du temps, et ne demande pas de savoir
quoi que ce soit sur le modèle recherché en dehors des noms de ses 
parents, ce qui est le plus souvent une information naturellement
présente dans le contexte d'appel.

Cependant, on peut vouloir désigner explicitement les parents que l'on 
spécifie 
(explicitement dire : je cherche le schéma oracle X sur l'instance oracle 
de nom TRUC sur le serveur ....). 
C'est particulièrement utile dans le cas d'un référentiel très toufu avec 
énormément de liens entre de tès nombreux composants.
Pour cela, on utilisera la *forme complète* de la notation.

------------
Syntaxe
------------

::

	model=nom_composant[,champ_parent=nom_parent[...]]|NOM_ENVT

Dénomination des champs : de même que pour la notation abrégée.

Vous observerez qu'il est devenu obligatoire de donner le modèle utlisé.
En effet, il serait difficile d'utiliser des noms de champ d'un modèle
sans connaitre le modèle. Ce modèle est donné en première position dans la liste,
et non indépendement comme dans la notation simplifiée.


------------
Résolution
------------

Mêmes remarques : toutes les données sont toujours utilisées.

De plus, une exception est levée si les noms de champs sont eronnés. 
(cela permet notamment de détecter plus facilement si vous ne remontez 
pas une branche unique de l'arbre généalogique)

*******************
Fonctions de l'API
*******************

.. warning:: 
	
	si vous ne précisez pas l'argument 'model' de ces fonctions,
	les composants retournés seront des objets :class:`Component`, donc 
	génériques !
	
	Pensez à utiliser leur attribut :attr:`leaf` si vous voulez utiliser
	les modèles spécifiques.

Des exemples sont donnés à la fin du document.


.. function:: getMCL(mcl [envt], [model])
	
	C'est la fonction principale de l'API. Elles est capable de prendre
	toutes les notations en entrée, que ce soit sous forme d'une chaîne de
	caractères ou d'une chaîne MCL décomposée en objets Python.
	
	Dans le cas où cette fonction reçoit une chaîne de caractère comme
	premier argument, tous les autres arguments sont non interprétés : la
	notation MCL est conçue pour contenir tous les éléments nécéssaires.
	
	Cette fonction s'appuie sur les fonctions suivantes :func:`getSimplifiedMCL`,
	:func:`getCompleteMCL`, :func:`filterMCL`.
	
	:arg mcl: Au choix : 
		
			* Chaîne de caractère de la notation MCL **simplifiée ou complète**\
			* Liste de tuples [(champ,nom),...] (notation complète)
			* Liste de chaînes de caractères [nom, nom_père, ...] (notation abrégée)
	
	:arg envt: Nom ou objet de l'environnement.
	:arg model: Nom ou classe du modèle à utiliser.
	
	:raise UnknownModel:
	:raise TooManyComponents:
	:raise UnknownComponent:
	:raise UnknownParent:

.. function:: filterMCL(mcl [envt], [model])
	
	C'est le pendant de la fonction getMCL. Elle retourne non pas un objet
	:class:`Component` unique mais une liste de ces objets.
	 
	Cette fonction est capable de prendre
	toutes les notations en entrée, que ce soit sous forme d'une chaîne de
	caractères ou d'une chaîne MCL décomposée en objets Python.
	
	Dans le cas où cette fonction reçoit une chaîne de caractère comme
	premier argument, tous les autres arguments sont non interprétés : la
	notation MCL est conçue pour contenir tous les éléments nécéssaires.
	
	Cette fonction s'appuie sur les fonctions suivantes :func:`getSimplifiedMCL`,
	:func:`getCompleteMCL`.
	
	:arg mcl: Au choix : 
		
			* Chaîne de caractère de la notation MCL **simplifiée ou complète**\
			* Liste de tuples [(champ,nom),...] (notation complète)
			* Liste de chaînes de caractères [nom, nom_père, ...] (notation abrégée)
	
	:arg envt: Nom ou objet de l'environnement.
	:arg model: Nom ou classe du modèle à utiliser.
	
	:return: une liste de composants, qui peut être vide.
	
	:raise UnknownModel:
	
	
.. function:: getSimplifiedMCL(mcl, [envt], [model])

	:arg mcl: Liste MCL simplifiée (i.e. liste de noms).
	:arg envt: Nom ou objet de l'environnement.
	:arg model: Nom ou classe du modèle à utiliser.
	
	:raise TooManyComponents: si la description n'est pas assez spécifique
	:raise UnknownComponent: si la description ne correspond à aucun composant.

.. function:: getCompleteMCL(mcl, [envt], [model])

	:arg mcl: Liste MCL (i.e. liste de doublets "champ=nom" ou de tuples (champ, nom)).
	:arg envt: Nom ou objet de l'environnement.
	:arg model: Nom ou classe du modèle à utiliser.
	
	:raise TooManyComponents: si la description n'est pas assez spécifique
	:raise UnknownComponent: si la description ne correspond à aucun composant.
	:raise UnknownParent: si un 'champ' précisé dans la liste n'existe pas dans les modèles parcourus.


*********************
API script shell
*********************

----------------------------
Script :program:`ask_ref.py`
----------------------------

C'est un script de requête du référentiel servant à intégrer le référentiel
de MAGE avec n'importe quel outil (principalement scripts de Gestion d'Environnement)
sachant appeler un script shell et parser un csv.
 
Code retour différent de 0 si composant introuvable, ou si erreur dans le 
formatage des données.

.. program:: ask_ref.py

.. cmdoption:: -t

	Afficher la liste des champs.
	Cette option est incompatible avec de multiples options -c.

.. cmdoption:: -c <MCL>, --components <MCL>
	
	Description d'un (ou de plusieurs, cf option -u) composant(s). Il peut y avoir
	plusieurs tags -c dans un même appel.

.. cmdoption:: -s <character>, --separator <character>

	Séparateur de colonne (défaut : point-virgule)
	
.. cmdoption:: -u, --unique

	Sortira en erreur si plus d'un seul résultat ou pas de résultats.
	Cette option est incompatible avec de multiples options -c.
	

Exemples : ::
	
	shell> ask_ref.py -c "dev1evt,GCDEV,XGCT1" -t -s "|"
	id|model|class_name|instance_name|component_ptr_id|password|
	17|oracleschema|Schema Gold Events|dev1evt|17||
	
	shell> ask_ref.py -c "dev1evt,GCDEV,XGCT1|DEV1|oracleschema" -s "|"
	17|oracleschema|Schema Gold Events|dev1evt|17||
	
	shell> ask_ref.py -c "Schema Gold Events|DEV1"
	17;oracleschema;Schema Gold Events;dev1evt;17;;

	shell> ask_ref.py -c "Schema Gold Events"
	17;oracleschema;Schema Gold Events;dev1evt;17;;
	18;oracleschema;Schema Gold Events;rec2evt;18;;
	
	shell> ask_ref.py -c "Schema Gold Events" -u
	Option unique precisee et plus d'un resultat
	

*********************
API web (TODO)
*********************
	
	
	
******************
Exemples API
******************

* Utilisation de la notation abrégée en n'utilisant que la généalogie :  ::

	>>> res = getMCL("P2,rec2evt,GCDEV,XGCT1")
	>>> print res
	Package P2 sur rec2evt
	>>> print type(res)
	<class 'MAGE.ref.models.Component'>
	>>> print type(res.leaf)
	<class 'MAGE.ora.models.OraclePackage'>

* Utilisation de la notation abrégée en précisant un nom de modèle : ::

	>>> res = getMCL("P2,rec2evt,GCDEV,XGCT1|OrAclePaCkage")
	>>> print res
	Package P2 sur rec2evt
	>>> print type(res)
	<class 'MAGE.ora.models.OraclePackage'>
  
  Notez ici que la casse n'a aucune importance dans le nom de modèle, et
  que le fait de préciser un nom de modèle fait que l'on reçoit un composant
  du bon type.
  
* Utilisation de la notation abrégée en précisant un nom de modèle et un environnement : ::

	>>> res = getMCL("P2,rec2evt,GCDEV,XGCT1|DEV2|OraclePackage")
	>>> print res
	Package P2 sur rec2evt
	>>> print type(res)
	<class 'MAGE.ora.models.OraclePackage'>
	
* Utilisation de la notation abrégée avec des objets Python : ::

	>>> res = getMCL(['P2','rec2evt','GCDEV','XGCT1'])
	>>> print res
	Package P2 sur rec2evt
	>>> print type(res)
	<class 'MAGE.ref.models.Component'>
	>>> print type(res.leaf)
	<class 'MAGE.ora.models.OraclePackage'>
	

