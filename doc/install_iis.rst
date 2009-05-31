##########################################
Installation de MAGE sous IIS 7 en FastCGI 
##########################################

Ce document présente rapidemment les étapes nécessaires pour faire 
tourner MAGE sous Windows. 

Il concerne principalement NT6 (Windows Vista SP1, 7, 2008 et 2008 R2), 
mais s'adapte facilement à Win2003 (IIS6).

****************
Préliminaires
****************

Vérifiez les :doc:`requirements`

********************
Choix de déploiement
********************

* Serveur FCGI threadé.
* Communication FCGI via pipe nommé. ("socket windows")
* Contrôle du serveur FCGI par IIS. (pas besoin de le démarrer par 
  ailleurs)
* Pas de réecriture d'URL.


*************************
Installation initiale
*************************

* Copier tous les fichiers dans un répertoire donné, par 
  exemple : C:\\MAGE.
* Ligne de commande, se placer dans le répertoire de MAGE.
* Exécuter : 
	* python install-debug-sqlite.bat si vous voulez démarrer 
	  rapidement avec une base sqlite contenant des données 
	  de démonstration
	* Sinon : 

		* Modifier le fichier settings.py pour renseigner les 
		  informations de connexion à une base de données. 
		* python manage.py syncdb   


****************************
Droits sur les répertoires
****************************

Il est comme toujours recommandé d'utiliser un compte utilisateur 
Windows aux droits minimaux dédié par site IIS.
 
Les droits minimaux sont :

* exécution sur python.exe, lecture sur l'ensemble des répertoires 
  Python (dont répertoires Django)
* lecture sur le répertoire MAGE.
 
 
**********************
Configuration d'IIS
**********************

Au choix, MAGE sera un sous-niveau du site par défaut 
(http://localhost/mage) ou un site dédié (du type http://domaine/mage). 
La seconde solution est recommandée, mais la configuration est similaire.

* Définir un nouveau pool d'application pour MAGE avec le compte 
  adéquat (si site dédié).
* Créer un nouveau site "MAGE" (si site dédié). Son répertoire 
  par défaut n'est pas important, car il ne contiendra que le 
  fichier web.config du site. Par exemple : C:\\inetpub\\MAGE
* Ecrire ou compléter le web.config en adaptant les chemins : ::

	<handlers accessPolicy="Read, Execute, Script">
		<add name="PYTHON" path="mage" verb="*" modules="FastCgiModule" scriptProcessor="C:\Python25\python.exe|C:\Users\user1\WebDjango\MAGE\MAGE\fcgi-wrapper.py" resourceType="Unspecified" />
	</handlers>
	<fastCgi>
		<application fullPath="C:\Python25\python.exe" arguments="C:\Users\user1\WebDjango\MAGE\MAGE\fcgi-wrapper.py" requestTimeout="10" activityTimeout="10" />
	</fastCgi> 
	
* Créer un nouveau répertoire virtuel "mediamage" pointant sur 
  %REPERTOIRE_MAGE%\media 
  (note : si vous modifiez le nom "mediamage", reportez le changement 
  dans settings.py)
* Créer un nouveau répertoire virtuel "adminmedia" pointant 
  sur %RépertoirePython%\Lib\site-packages\django\contrib\admin\media 
  (même remarque que précédemment)


Tester, fin de l'installation.

****************
Notes diverses
****************

* Le choix de "mage" comme préfixe des URL est arbitraire, et peut 
  être changé à loisir.
* On peut adapter, dans le web.config, le nombre de threads, la 
  longueur maximale des file d'attente FCGI, etc.
* Les fichiers de config FCGI d'IIS 6 sont de type .ini (donc hors 
  metabase), mais leur contenu est similaire.
* Il est tout à fait possible d'utiliser un port TCP plutôt qu'un pipe 
  nommé pour la communication entre IIS et Django. Non testé. Cela 
  demanderait des changements dans le wrapper FCGI.
* De la même façon, il est facile de passer d'un serveur FCGI threadé à 
  un serveur qui forque en modifiant le wrapper.
* Django est livré avec un wrapper FCGI basé sur flup, non supporté et 
  pas vraiment fonctionnel sous Windows. Il vaut mieux ne pas l'utiliser
  comme le fait cette doc. 