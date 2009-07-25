###########################
API gestionnaire de ticket
###########################

.. module:: MAGE.tkl
	:synopsis: Link with ticket management systems (TKMS)
.. moduleauthor:: Marc-Antoine Gouillart 

.. warning:: Ceci est un **document de conception**, pas encore une doc utilisable.

***********************
Fonctions attendues
***********************

La GE se fait souvent en conjonction avec un gestionnaire de tickets.
MAGE se doit donc d'offrir certaines fonctionalités permettant d'exploiter
les informations contenues dans ce gestionnaire de ticket et ainsi d'éviter 
des doubles saisies et faciliter le suivi.

Les attendus fonctionnels sont les suivants :

* Changement automatique de l'état d'un ticket dans le TKMS lors des
  opérations de GCL (installation de patch, chargement sauvegarde...)
* Donner directement un aperçu de tous les tickets à traiter par
  l'équipe de GE.
* Pouvoir directement ajouter des notes à une fiche.

Ce document décrit l'interface attendue par MAGE, telle qu'elle doit être
implémentée par un nouveau module. L'API réside dans le module 
:mod:`MAGE.tkl` (tkl = TicKet Link)


**************************
Choix de conception divers
**************************

Nous refusons strictement de devoir taper un mot de passe à chaque 
opération de GCL... il sera donc impératif d'avoir un compte unique pour 
toutes les opération réalisées via MAGE. (cela est bien entendu sans
objet si vous utilisez un accès sans compte au TKMS...)

Ce compte sera au choix créé automatiquent par le module lors de son
utilisation, ou manuellmeent (faire une belle doc d'install).

Aucune contrainte n'est imposée dans les modes de communication avec
le TKMS : API Python, C, web service, ... Si vous utilisez un module
Python particulier, n'oubliez pas de le rajouter aux pré requis de votre
module.

.. note:: 

	Comment MAGE va-t-il savoir quel module utiliser ?
	
	Bon, bah c'est pas très beau... Mais vous allez simplement
	créer un :class:`MageParam` dont la valeur sera votre module, sur le modèle: ::
	
		MageParam(	key = "TKL_MODULE", 
					app = "votre app",
					description = u"Module utilisé pour communiquer avec un gestionnaire de ticket")
	
Pour tout ce qui est paramétrage (logins, nom du champ à mettre à jour, etc) :
utilisez le module du coeur :mod:`MAGE.prm`
  
L'utilisation du système sera coûteuse au niveau performance et mise en place, et 
peut-être inutile pour beaucoup. Un paramètre général (clé : ENABLE_TKmS_LINK,
application tkl, valeur true ou false (défaut)) contrôlera le 
fonctionnement global du lien. Pensez à le mentionner dans votre doc. 


************************
Objets de base de l'API
************************

.. class:: Ticket

	Les instances de cette classe représentent des tickets contenus dans
	le TKMS.
	Sauf exception, les champs sont en lecture/écriture dans la classe. Cependant, les
	informations ne sont répercutées dans la base qu'après un appel à
	:meth:`flush`.
	
	Cette classe soit impérativement être surchargée dans les modules
	spécifiques, **sous le nom de Ticket** 
	
	Les instances de :class:`Ticket` ont les méthodes suivantes :
	
	.. method:: Ticket.refresh()
	
		Va chercher les informations dans le TKMS. Ecrase les données
		locales, même si elles ont été modifées.
		
		.. todo:: Lance des exceptions diverses et à préciser.
		
		:rtype: None
		
	.. method:: flush()
	
		Ecrit les valeurs locales dans le TKMS.
		
		:raises: :exc:`TKMSOperationNotAllowed` si les droits du compte
			utilisé n'autorisent pas l'opération
		:raises: :exc:`TKMSOperationFailed`
		
		:rtype: None
	
	.. attribute:: id
	
		Le numéro identifiant le ticket dans le TKMS. En **lecture seule**\ .
		
		.. note:: La condition lecture seul est à implémenter absolument
		
		:type: entier naturel
		
	.. attribute:: title
		
		:type: chaine unicode
		
		Titre du ticket
		
	
	.. attribute:: description
	
		:type: chaine unicode
	
	.. attribute:: reporter
	
		:type: chaine unicode
	
	.. attribute:: affected_to 
		
		:type: chaine unicode


*****************************
Fonctions statiques
*****************************

.. function:: getTicket(ticket_id)
	
	:param: ticket_id
	:raise: :exc:`TicketDoesNotExist` (ticket_id) si existe pas
	:raise: :exc:`TKMSOperationNotAllowed` si les droits du compte
			utilisé n'autorisent pas l'opération
	:raise: :exc:`TKMSOperationFailed` pour les autres cas d'erreur liés au module
	:return: the required ticket
	
.. function:: getTickets([ reporters ], [status], [since])

	:param: reporters filter the results with the given list of reporters
	:param: status filter the results with the given list of status
	:param: since filtrer tout ce qui est < au paramètre.
	:raise: :exc:`TKMSOperationNotAllowed` si les droits du compte
			utilisé n'autorisent pas l'opération
	:raise: :exc:`TKMSOperationFailed` pour les autres cas d'erreur liés au module
	:return: une liste de :class:`Ticket`, potentiellement vide.
	
