==========================
La gestion des paramètres
==========================

.. module:: MAGE.prm.models
	:synopsis: Parameter handling module
.. moduleauthor:: Marc-Antoine Gouillart 


Les différents modules ont souvent besoin de stocker les valeurs
de certains paramètres qui doivent être librement modifiables par
l'administrateur.

Mage propose donc un module de gestion unifiée des paramètres, pour rendre leur
gestion plus simple tant pour l'administrateur que pour le développeur.


**************************
L'objet :class:`MageParam` 
**************************


.. class:: MageParam

	.. attribute:: key
	
		C'est l'identifiant du paramètre. (Chaîne de caractères)
		
	.. attribute:: app
	
		Nom de code de l'application utilisant le paramètre.
		
	.. attribute:: value
	
		Valeur du paramètre. Stocké dans une chaine de caractères.
	
	.. attribute:: description
	
		Phrase décrivant le paramètre et son rôle.

	.. attribute:: default_value
	
		Attribut optionnel, déstiné à contenir la valeur par défaut du paramètre.
		
	.. attribute:: model
	
		Attribut optionnel. Certains paramètres devront être instanciés par modèle.
		Par exemple, il peut exister un :class:`MageParam` désignant le type de node
		graphviz à utiliser par modèle.
		
	.. attribute:: axis1
	
		Attribut optionnel. Autre axe d'instanciation (celui-ci libre) des paramètres. Cf. :attr:`model`.
		
		.. warning::
			
			Cet axe ne devrait pas avoir à être utilisé en dehors de cas exceptionnels.


***************
API associée 
***************

.. function:: getParam(key, **filters)

	C'est la fonction à utiliser pour récupérer la valeur d'un paramètre.
	
	Elle a besoin au minimum de la clé. 
	
	Si vous ne précisez pas l'application dans les filtres, la fonction 
	récupère l'application dans laquelle est placée la fonction qui a
	effectué l'appel. (cela ne marche donc que si l'appel a lieu depuis
	une application de MAGE, et non un script indépendant).
	
	:parameter key: Obligatoire. Clé du paramètre.
	:type key: ustring 
	:parameter filters: Optionnel. Toute association du type clé=valeur.
	:type filters: {ustring:ustring,}
	
	:returns: la valeur du paramètre.
	:rtype: ustring
	
	:raises ParamNotFound: Si un paramètre est introuvable avec les arguments fournis.
	:raises DuplicateParam: Si les critères de sélection fournis renvoient plus d'un résultat.
	
	Par exemple : ::
	
		>>> getParam(key = 'SUPER_PARAM', app = 'ora', axis1 = 'meuh')
		'pouet'

.. function:: setParam(key, value, **params)

	C'est le pendant de :func:`getParam`. Voir cette fonction pour les détails.
	
	Exemple : ::
	
		>>> setParam('SUPER_PARAM', app='ora', axis1 = 'meuh', value = 'pouet')
		
.. function:: getMyParams()

	Cette fonction est strictement réservée aux applications MAGE.
	
	Elle retourne un ResultSet contenant tous les paramètres de l'application
	appelant cette fonction.
	
	C'est une fonction utile si vous allez faire plein d'opérations sur les
	paramètres, par exemple au sein de boucles.
	En effet, les appels à :func:`getParam` font systématiquement
	un appel à l'ORM, donc cette fonction ne doit pas être utilisée dans une
	boucle.


************************
Administration associée 
************************

Les paramètres sont exclusivement destinés à être modifiés via l'interface d'administration.
