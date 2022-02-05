# coding: utf-8
'''
    @license: Apache License, Version 2.0
    @copyright: 2007-2013 Marc-Antoine Gouillart
    @author: Marc-Antoine Gouillart
'''

# Python imports

# Django imports

# MAGE imports
from ref.models.parameters import setOrCreateParam
from ref.permissions.perm_sync import sync_project_perms


def post_migrate_handler(sender, **kwargs):
    '''All actions that must be taken by the ref app when database migrate has run'''
    # Create or update parameters

    # General parameters that should never be removed...
    setOrCreateParam(key='LINK_COLORS', value='#004D60,#1B58B8,#DE4AAD,#D39D09,#AD103C,#180052',
                     default_value='#004D60,#1B58B8,#DE4AAD',
                     description='Couleurs des liens de la page d\'accueil')

    setOrCreateParam(key='MODERN_COLORS', value='#004A00,#61292B,#180052,#AD103C,#004D60,#1B58B8,#DE4AAD',
                     default_value='#004A00,#61292B,#180052,#AD103C,#004D60,#1B58B8,#DE4AAD',
                     description='Couleurs des cases de la page d\'accueil')

    # Welcome screen parameters
    setOrCreateParam(key='LINKS_TITLE', value='Liens utiles',
                     default_value='Liens utiles',
                     description='titre du bloc de liens sur la page d\'accueil',
                     axis1='welcome')

    # Redo permissions just in case.
    sync_project_perms()

    # DEBUG
    # create_full_test_data()
