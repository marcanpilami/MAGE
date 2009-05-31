###########
Pré requis
###########

*************
Pour le coeur
*************

* Python 2.4, 2.5 ou 2.6 : www.python.org
* Django 1.0.2 (http://www.djangoproject.com/)
* Les mappings nécessaires pour se connecter à votre base de données
  en Python.
  (sqlite est installé par défaut avec Python 2.5 et 2.6)
* Un compte de base de donnée qq part, droits ???


*************************
Pour utiliser les graphes
*************************

* Graphviz
* pydot-1.0.2

*****************************
Pour un déploiement FastCGI
*****************************

* La bibliothèque FastCGI Python (http://cheeseshop.python.org/pypi/python-fastcgi)
* La DLL FastCGI officielle (http://hivcc.com/python/fastcgi/libfcgi.dll), à placer directement dans le répertoire de Python (ex : C:\Python25)
* Module FastCGI pour votre serveur web.
	* Vista : il faut installer le SP1 pour utiliser le FastCGI.
	* Windows 2008 : le module FastCGI est à télécharger sur www.iis.net.
	* Windows 2008 R2 ou 7 : tout est bon de base.
