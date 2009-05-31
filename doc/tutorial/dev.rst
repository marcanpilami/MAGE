####################
Tutorial développeur
####################

************
Introduction
************

MAGE est un framework fournissant un certain nombre d'éléments visant à 
faciliter la gestion des environnements. Mais ce n'est qu'un framework, 
il ne peut pas deviner en quels composants vous avez découpé votre 
environnement ni quels éléments de description vous sont utiles. 
Il y a donc nécessairement besoin d'indiquer à MAGE
les composants que vous utilisez, et les informations qui leurs sont
relatives.
 
Le but de ce tutorial est de vous apprendre à développer les éléments 
MAGE nécessaires à la gestion d’un nouveau type de composant.

Ce document va s’attacher à créer l’application Oracle de MAGE. 
Cette application étant livrée finie dans la version .git de MAGE, 
vous pourrez vous référer au code complet.

*************************
Connaissances préalables
*************************

Ce tutorial suppose une connaissance de base de Python et de Django.

Se référer aux sites suivants :

* `Python <http://python.org>`_
* `Django <http://djangoproject.org>`_ (faites le tutorial)

Il suppose également que vous ayez lu la section :doc:`../structure_interne`.


********************
L'application Oracle
********************

==============
Besoin exprimé
==============

Le première chose à faire, dans le cadre de la GE, est de définir ce
qu'on apelle un "composant", i.e. la granularaité du suivi qu'on va
effectuer.

Dans notre cas, les hypothèses sont les suivantes.

Le projet comporte de nombreux éléments Oracle. Le gestionnaire 
d’environnement a en particulier sous sa responsabilité (ou bien il 
exploite) :

* Des instances (gérées par les DBA)
* Des schémas
* Des modèles de données. (MPD) (avec index, etc.)
* Des packages
* Des fonctions
* Des tablespaces (géré par les DBA)

Le projet est en phase de développement, et régulièrement, la GE reçoit des paquets à installer. Ils concernent MPD, packages. Les fonctions ne sont jamais re livrées. Chaque package a son propre numéro de version. Le MPD a un numéro de version global.

De plus, le gestionnaire d’environnement désirerait :

* Centraliser les informations de connexion pour se soulager de 
  milliers de demandes idiotes.
* Automatiser l’application des paquets reçus des développeurs.


===============================
Analyse du besoin (A COMPLETER)
===============================

Nous allons donc créer une nouvelle application Django. Son nom sera 
« ora » (3 lettres, simple convention de nommage).

Presque tous les éléments précités donneront lieu à un composant (CI) 
dans MAGE car ou bien ils vont devoir être suivi en version, ou bien 
ils comportent des informations de connexion indispensables.

Seuls le tablespace et les fonctions n’ont pas besoin de composant 
dédié.

==========================
Création du nouveau module
==========================

En ligne de commande, se placer à la racine de Mage.
Exécuter : ::

	python manage.py startapp ora

Note : il n'est le plus souvent pas nécessaire de préciser "python"
dans ces lignes de commande, mais sous Windows on peut avoir des 
associations fantaisistes du suffixe .py avec des éditeurs et non
python.exe. Nous le préciserons donc systématiquement.

====================
Création des modèles
====================

Dans notre cas, nous aurons :

* Instance Oracle
* Schéma Oracle
* Package Oracle
* MPD

Un composant MAGE n’est qu’une simple spécialisation de la classe 
« Component » du paquetage du cœur « ref ». Les règles d’héritage 
classiques s’appliquent ici, et l’ORM se débrouille tout seul pour 
raccrocher les morceaux.

La classe Component dont on dérive comporte déjà des champs de base pour
le nom de classe et le nom d’instance (cf. schéma plus haut). Les deux 
ne sont pas obligatoires.
Pour l’instance oracle, seul le nom d’instance est intéressant. 
Par contre, pour un schéma Oracle, on pourra avoir besoin des deux : 
la classe pourra par exemple être « gestion des canidés » ou encore 
« gestion des monotrèmes », tandis que le nom d’instance sera le nom 
du schéma (login). C’est important de les classifier ainsi, car si cela 
reste dans les deux cas un schéma Oracle, il faut que Mage puisse savoir qu’ils ne doivent pas être gérés de la même manière. En particulier, un patch corrigeant les pieds des canidés aura peu de chance de fonctionner sur les pieds des monotrèmes (tous étant palmés à une exception près), et cela permettra à Mage de protester bruyamment en cas de tentative inopportune d’application.
On pourrait bien sûr aussi envisager d’avoir différentes classes 
d’instances, mais ne nous compliquons pas la tâche.

Le nom de classe est un champ texte libre. Attention aux fautes de 
frappe si vous utilisez l’interface d’administration ! 

Dans le fichier ora/models.py, on aura simplement pour l’instance : ::

	class OracleInstance(Component):
	    port = models.IntegerField(max_length=6, verbose_name=u"Port d'écoute du listener")
	    listener = models.CharField(max_length=100, verbose_name=u'Nom du listener')
		
On retrouve ici la définition des champs d'un modèle classique de Django
(longueur maximale, description en langue compréhensible...).
Et c'est tout ce qui suffit pour un fonctionnement minimal !

==========================================
Plus loin dans la description du composant
==========================================

Django et MAGE utilisent très souvent l’introspection des modèles, 
notamment pour l’interface d’administration. Pour débloquer toutes les 
fonctionalités de l'outil, il faut aller un peu plus loin dans la
description du modèle.

-----------------------------------------
Décrire tous les champs
-----------------------------------------

Pour tous les champs, même si vous ne voulez pas l'afficher dans la
console d'administration, renseignez "verbose_name": ::

	port = models.IntegerField(max_length=6, verbose_name=u’Port utilisé par le listener’)	

Notez le « u » précédant la chaîne, qui indique une chaîne Unicode. 
(MAGE est entièrement en Unicode, veillez à encoder tous vos fichiers 
ainsi).

------------------------------------------
Décrire tous les modèles
------------------------------------------

De plus, le nom du modèle, s’il est pratique pour les programmeurs, 
peut paraitre peu clair pour un utilisateur final, on va donc indiquer 
une description. Pour cela, on rajoute une sous classe au modèle 
nommée « meta ». ::

	class Meta:
		verbose_name = u'Instance de base de données'
		verbose_name_plural = u'Instances de base de données'

La version du modèle à cette étape est donc : ::

	class OracleInstance(Component):
		port = models.IntegerField(max_length=6, verbose_name=u'Port d\'écoute du listener')
		listener = models.CharField(max_length=100, verbose_name=u'Nom du listener')
    
		class Meta:
			verbose_name = u'Instance de base de données'
			verbose_name_plural = u'Instances de base de données'

--------------------------------
Décrire l'ascendance des modèles
--------------------------------

Dans la description retenue, une instance Oracle n’a qu’un seul 
« parent » : un serveur. Cet objet est un composant très basique fourni 
en standard avec Mage. (Note : comme pour tout composant livré avec 
MAGE, c’est une démo, pas un composant utilisable directement en 
production)

Nous avons dit que les parents et autres collaborateurs étaient déjà 
gérés par le modèle Component du cœur de Mage. C’est vrai, mais il 
n’est pas toujours pratique d’utiliser cette relation, car la requête 
n’est pas des plus évidentes : ::

	self.dependsOn.get(model__model='server').leaf

Pour compenser ce désagrément du au caractère extrèmement générique de
la modélisation, MAGE ajoute automatiquement des propriétés à vos
modèles pour permettre un accès rapide à ses parents, pour peu que vous
lui donniez leur description, sous la forme : ::

	parents = {'instance':'OracleInstance'}

* parents est un nom obligatoire.
* instance est le nom du nouveau champ.
  ATTENTION : il faut prendre un nom qui n'existe pas déjà dans le modèle,
  en particulier pas un nom de modèle !
* OracleInstance est, en texte simple, le nom de la classe du modèle 
  du parent de nom 'instance'.
* Il peut y avoir autant de parents que vous voulez.

Ce champ est utilisé : 

* dans la GCL.
* pour valider les instances de modèle (pas de parents présents d'un 
  modèle qui ne soit pas dans la liste).
* dans certains cas, lorsqu'un module doit créer automatiquement une
  instance d'un modèle.

Si ce champ n'est pas précisé (ce qui est différent de parents={}),
aucune propriété n'est crée et aucune validation de cohérence n'est 
effectuée.

====================================
Application d'admin
====================================

Le tutorial Django vous aura appris à associer à vos modèles une classe
dérivée de admin.ModelAdmin.
Le principe ne change pas dans MAGE, sauf qu'il est recommandé de dériver
votre classe d'administration de CompoAdmin (dans MAGE.ref.admin), qui
elle même dérive de admin.ModelAdmin.

En effet, cette classe fournit une configuration de base (filtres, 
champs, ...) et de plus exploite le champ "parents" pour filtrer les
listes de composants. ::

	class OracleInstanceAdmin(ComponentAdmin):
		ordering = ('instance_name',)
		list_display = ('instance_name',)# 'server',)
		search_fields = ('instance_name',)
		fieldsets = [
			('Informations génériques',  {'fields': ['instance_name', 'dependsOn']}),
			('Informations Oracle',  {'fields': ['port', 'listener']}),
			]

=====================
Création d'un rapport
=====================

Nous avons vu la partie « modèle » de Django. A présent, intéressons 
nous aux parties « VC », ou plutôt Vues (grossièrement équivalent au 
contrôleur) et Templates (de même avec la vue).
La vue est chargée des traitements et de renvoyer une réponse, qui peut 
aussi bien être une page HTML qu’un CSV, une image, etc.…
Par exemple, le marsupilamographe a des vues qui génèrent des 
formulaires HTML, et d’autres qui génèrent les images décrites dans les 
formulaires.
Le moteur de templates est chargé, à partir d’un template défini dans 
un très simple langage spécifique, de mettre en page des informations 
fournies par une vue. Ces inforamtions fournies s’appellent un contexte. (le template est donc appelé par la vue)

Pour éviter de devoir systématiquement préciser les chemins complets 
des templates, veuillez toujours préfixer le nom des templates par le 
nom de l’application, ce qui empêchera toute confusion.


Note : le tutorial Django vous a appris à placer tous les templates de 
toutes les applications dans un répertoire particulier, et à centraliser
les urls dans un fichier commun. Mage ne procède pas ainsi : tous vos 
templates sont à placer dans un répertoire « templates »  de votre 
application, et les urls dans un fichier urls.py situé à la racine de 
cotre application. Cela permet d’avoir des applications très 
indépendantes et faciles à déployer.

-----------------
But du rapport
-----------------

Imaginons que les DBAs veuillent un point régulier sur l’ensemble des 
schémas contenus dans toutes les instances. C’est assez idiot, mais ça 
fait un bon exemple.
Le contexte est très simple : une simple liste des instances. On n’a 
pas besoin de lister les schémas, vu que les schémas sont déclarés 
enfants des instances. Cependant, on va tout de même ajouter une liste 
des schémas non rattachés à une instance, cela permettra de détecter 
les incohérences dans la base.


--------------
Code de la vue
--------------

C'est une vue nromale, telle que vous avez pu les voir dans le tutorial
Django. ::

	# coding: utf-8
	
	## Django imports
	from django.shortcuts import render_to_response
	
	## MAGE imports
	from MAGE.ora.models import OracleInstance, OracleSchema
	    
	def dba_edition(request):
		"""Liste des schémas par instance Oracle"""
		instance_set = OracleInstance.objects.all()
		unclassified_schemas = OracleSchema.objects.all().exclude(dependsOn__model__model='oracleinstance') 
		return render_to_response('ora_dba_edition.html', {'instance_set':instance_set, 'us':unclassified_schemas})
		
--------
Template
--------

De même, rien d'exceptionnel ici.
Pour les templates HTML, MAGE propose de faire hériter votre template 
d’un template de base, qui comporte déjà toutes les balises de base, 
une CSS, etc. Cela permet de conserver un aspect uniforme à travers 
toute l’application.
Ce template définit un certain nombre de blocs que les templates 
enfants peuvent remplacer. ::

	{% extends "base.html" %}
	{%block pagetitle%}Rapport DBA{%endblock%}
	{%block maintitle%}Rapport DBA{%endblock%}
	{%block content%}
		{% for inst in instance_set %}
			<div class='bloc2'>
				<div class='t3'>{{inst.instance_name}}</div>
				{% for component in inst.subscribers.all %}
					<div class='t4'> {{component}}</div>
				{% endfor %}
			</div>
		{% endfor %}
		{%if us %}
			<div class='bloc2'>
				<div class='t3'>Non classifié</div>
				{% for schema in us %}
					<div class='t4'> {{schema}}</div>
				{% endfor %}
			</div>
		{% endif %}
	{%endblock%}
	

Quelques commentaires :

* La première signale que l’on va hériter du template MAGE de base.
* La deuxième ligne met le texte « Rapport DBA » dans le bloc « pagetitle » du template de base. C’est bien entendu le titre de la page (au sens HTML)
* De même pour la troisième ligne, qui met le même texte dans la partie « maintitle » du template de base, i.e. son « grand titre ».
* Ligne 4 à la fin : c’est le contenu même de la page.

	* Ligne 5 à 12 : boucle sur tous les éléments contenus dans l’élément du contexte « instance_set ».
	* Ligne 7 : les doubles accolades signalent que l’on veut la valeur correspondant à l’expression. On observe qu’on a accès à toutes les options de navigation de Django, on pourrait suivre toutes les FK, etc. On peut aussi directement utiliser des fonctions.

* Le bloc « if » n’est pas un « if » classique de programmation. (le template devant se limiter à de la présentation). Il dit simplement que si l’élément passé en paramètre existent alors la suite sera affichée. Dans notre cas, le cadre « Non classifié » ne sera affiché que s’il y a des éléments non classifiés.


Enfin, on renvoie ici de l'HTML, mais on peut créer des CSV, des images...


---
URL
---

Toutes les URL de votre application doivent impérativement être placées 
dans un fichier urls.py situé à la racine de l’application.
Au démarrage de MAGE, celui-ci les collectera et les préfixera par le 
nom de l’application.

Dans notre cas, le fichier ora/urls.py sera : ::
	
	# coding: utf-8
	
	from django.conf.urls.defaults import *
	
	urlpatterns = patterns('',
		(r'dba$', 'MAGE.ora.views.dba_edition'),
	)

Notez que les expressions régulières :

* Sont précédées par « r ». cela signifie « raw string », ce qui 
  permet de ne pas protéger par un « \ » les caractères spéciaux pour 
  Python.
* Ne commencent jamais par « ^ », car il ne s’agit là que de la fin de 
  l’adresse.

Ainsi, notre vue sera appelée via l’adresse :
`http://RACINE/SITE/ora/dba` 

De plus, vous observerez que cette URL ne fait aucune hypothèse sur la 
première partie de l’URL. Souvent, le déploiement se fera avec un 
préfixe pour chaque adresse. C’est géré automatiquement par Django et 
Mage.

Notez que toute URL utilisable sans arguments est automatiquement 
rajoutée à la liste des pages.. La description affichée est la 
documentation de la fonction vue. (i.e. texte placé entre trois paires 
de guillemets doubles la ligne suivant la déclaration de la fonction).
`http://RACINE/MAGE/listepages` 


-----
Liens
-----

Si l’on ne connait pas les adresses complètes à cause des préfixes, 
comment lier des pages entre elles ?
Il faut utiliser la fonction reverse dans les vues, ou le tag de 
template {%url%}, qui permettent, à partir du nom de la  vue ou d’un 
mot clé, de générer l’adresse.
Ainsi, on se prémunit même contre les changements d’URL.

L'utilisation de ces éléments est obligatoire : vous n'avez aucune
idée du mode de déploiement choisi pour MAGE par les utilisateurs de 
votre module.

=========================
Intégration au module PDA
=========================

Nos nouveaux éléments ne sont pas affichés sur la page d’accueil 
publique. Cela peut bien entendu être une volonté du programmeur que de 
ne pas tout afficher sur cette page. Par exemple, afficher tous les 
packages d’un environnement sur cette page se voulant synthétique 
serait ridicule.
MAGE donne donc le choix d’afficher ou non les éléments sur la page 
d’accueil. Si on ne désire rien, il n’y a rien à faire.
Sinon, il faut rajouter un champ statique « detail_template » au modèle,
qui contient le nom (ou le chemin complet) du template à utiliser pour 
représenter l’élément sur la page d’accueil.

On désire afficher les schémas sur la page d’accueil. On rajoute donc à 
leur modèle : ::

	detail_template = 'ora_schema_details.html'

Note : ces références et templates pourraient à l’avenir être utilisées 
par d’autres applications fournies avec MAGE.

Le template est à construire normalement, et à placer dans le répertoire
templates de l’application. 
Son contexte est un simple objet « comp », désignant le composant. Il 
sera rendu au sein d’un bloc « div », vous n’avez pas à vous soucier 
d’hériter d’un autre template, de balises « <html> », etc.
De plus, les parents et la version du composant (le cas échéant) seront 
affichés par le module PDA lui-même.
N’oubliez pas qu’on peut naviguer le long des relations. Pour la 
démonstration, on affichera plein d’éléments assez inutiles : ::

	<div>
		<span class='t4'>Login : {{comp.instance_name}}</span><br/>
		<span class='t4'>Liste des packages installés :</span><br/>
		{% for pck in comp.subscribers.all %}
			<ul class="liste1">
				<li>{{pck.class_name}}</li>
			</ul>
		{% endfor %}
	</div>


======================
Installation du module
======================

Votre composant est prêt à être utilisé. Il ne manque plus que d’activer 
l’application dans MAGE.
Pour ce faire, ouvrez le settings.py situé à la racine de l’arborescence
Mage, et rajoutez la ligne correspondant à votre application à la fin 
de la liste au bas du fichier.

Pour le rédacteur de ce document, la liste est : ::

	INSTALLED_APPS = (
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.sites',
		'django.contrib.admin',
		'MAGE.ref',
		'MAGE.gph',
		'MAGE.srv',
		'MAGE.mqqm',
		'MAGE.gcl',
		'MAGE.liv',
		'MAGE.sav',
		'MAGE.pda',
		'MAGE.fif',
		'MAGE.ora',
	)
	
La liste pourra bien entendu être différente sur votre machine.

L’ordre de ce tuple est important ! Par précaution, toujours rajouter 
votre application à la fin, ou au minimum après toute application dont 
vous utiliseriez des éléments. Dans notre cas, il faut être après les 
applications cœur de Mage et après srv (contenant le Server).
