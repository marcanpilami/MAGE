# coding: utf-8

"""
    Minimalist Ticket Manager initialisation file.
    
    @warning: This is not done, and should no be used. (and is of little interest)
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Python imports

## Django imports
from django.db.models.signals import post_syncdb
from django.db import transaction

## MAGE imports
import models
from MAGE.prm.models import setParam, getMyParams
from MAGE.tkm.models import TicketClass, ListElement, FieldDisposition, TF_List, TF_Text, TF_ShortText,\
                             TabularSummary, SummaryBlock, Workflow, State, Transition, TF_EnvtList,\
                             TF_User, TF_Group

@transaction.commit_manually
def createDefaultTicketClass():
    ## Create ticket type
    tc = TicketClass(name='Ticket de demande d\'intervention')
    tc.save()

    ## Priority
    tcf1 = TF_List(name=u'Priorité', 
                  description=u'Indication pour la priorisation du traitement du ticket.')
    tcf1.save()
    ListElement(elt = u'urgent', level=100, parent_list = tcf1).save()
    ListElement(elt = u'normal', level=50, parent_list = tcf1, default = True).save()
    ListElement(elt = u'peut attendre', level=1, parent_list = tcf1).save()
    FieldDisposition(ticket_class = tc, field = tcf1, group = u'1 : Désirs utilisateur', position = 1).save()

    ## Environment
    tcf2 = TF_EnvtList(name = u'Environnement',
                      description = u'Sélection d\'un environnement')
    tcf2.save()
    FieldDisposition(ticket_class = tc, field = tcf2, group = u'2 : classification GE', position = 3).save()

    ## Impact
    tcf3 = TF_List(name=u'Sévérité', 
                  description=u'Indication sur le caractère ennuyeux de l\'incident.')
    tcf3.save()
    ListElement(elt = u'pas grave', level=1, parent_list = tcf3).save()
    ListElement(elt = u'ennuyeux', level=50, parent_list = tcf3, default = True).save()
    ListElement(elt = u'super bloquant', level=100, parent_list = tcf3).save()
    FieldDisposition(ticket_class = tc, field = tcf3, group = u'1 : Désirs utilisateur', position = 2).save()

    ## Resolution
    tcf5 = TF_List(name=u'Résolution', 
                  description=u'Qu\'en est-il de la résolution de ce ticket ?',
                  compulsory = False)
    tcf5.save()
    ListElement(elt = u'résolu', level=100, parent_list = tcf5).save()
    ListElement(elt = u'ticket invalide', level=10, parent_list = tcf5).save()
    ListElement(elt = u'ne sera pas résolu', level=10, parent_list = tcf5).save()
    ListElement(elt = u'duplicata', level=10, parent_list = tcf5).save()
    ListElement(elt = u'non reproductible', level=10, parent_list = tcf5).save()
    FieldDisposition(ticket_class = tc, field = tcf5, group = u'2 : classification GE', position = 5).save()

    ## Description
    tcf6 = TF_Text(name = u'Description', description = u'Description du ticket')
    tcf6.save()
    FieldDisposition(ticket_class = tc, field = tcf6, group = u'3 : Blabla', position = 2, cr = True).save()
    
    ## Commentary
    tcf7 = TF_Text(name = u'Commentaire', 
                   description = u'Commentaire supplémentaire adjoint au ticket', 
                   compulsory = False)
    tcf7.save()
    FieldDisposition(ticket_class = tc, field = tcf7, group = u'3 : Blabla', position = 3).save()
    
    ## Title
    tcf8 = TF_ShortText(name = u'Titre', description = u'200 caractères pour retenir l\'attention de l\'admin...')
    tcf8.save()
    FieldDisposition(ticket_class = tc, field = tcf8, group = u'3 : Blabla', position = 1, cr = True).save()
    
    ## Category
    tcf9 = TF_List(name=u'Catégorie', 
                  description=u'Catégorisation supplémentaire',
                  compulsory = False)
    tcf9.save()
    ListElement(elt = u'inutile', level=2, parent_list = tcf9, default = True).save()
    ListElement(elt = u'moyennement utile', level=20, parent_list = tcf9).save()
    ListElement(elt = u'utile', level=50, parent_list = tcf9).save()
    ListElement(elt = u'profondément inutile', level=1, parent_list = tcf9).save()    
    
    
    ## Affected to user & group
    tcf10 = TF_User(name=u'affecté à', description = u'ce ticket est actuellement traité par', 
                    compulsory = False)
    tcf10.save()
    FieldDisposition(ticket_class = tc, field = tcf10, group = u'2 : classification GE', position = 12).save()
    
    tcf11 = TF_Group(name=u'affecté au groupe', description = u'ce ticket est actuellement traité par',
                     compulsory = False)
    tcf11.save()
    FieldDisposition(ticket_class = tc, field = tcf11, group = u'2 : classification GE', position = 13).save()


    ## Report list
    r = TabularSummary(name = u'Rapport par défaut')
    r.save()
    b1 = SummaryBlock(summary = r)
    b1.save()
    b1.fields = [tcf8, tcf2, tcf3,]
    
    transaction.commit()
 
@transaction.commit_manually 
def createDefaultWorkflow():
    ## New workflow
    tcf4 = Workflow(name=u'Statut', 
                    description=u'cheminement standard d\'une fiche chez un compte normal...')
    tcf4.save()
    
    ## Workflow states
    nouveau  = State(name = u'nouveau', level=1, workflow = tcf4, start = True)
    attribue = State(name = u'attribué', level=10, workflow = tcf4)
    reouvert = State(name = u'ré-ouvert', level=50, workflow = tcf4)
    ferme    = State(name = u'fermé', level=100, workflow = tcf4)
    nouveau.save(); attribue.save(); reouvert.save(); ferme.save()
    
    ## Add the workflow to the default ticket class
    tc = TicketClass.objects.get(name='Ticket de demande d\'intervention')
    FieldDisposition(ticket_class = tc, field = tcf4, group = u'2 : classification GE', position = 5).save()

    ## Add the workflow to the default report
    r = TabularSummary.objects.get(name = u'Rapport par défaut')
    r.blocks.all()[0].fields.add(tcf4)
    
    ## WF transitions
    t1 = Transition(target_state = attribue, source_state = nouveau)
    t2 = Transition(target_state = ferme, source_state = nouveau)
    t3 = Transition(target_state = ferme, source_state = attribue)
    t4 = Transition(target_state = reouvert, source_state = ferme)
    t5 = Transition(target_state = attribue, source_state = reouvert)
    t6 = Transition(target_state = ferme, source_state = reouvert)
    t1.save(); t2.save(); t3.save(); t4.save(); t5.save(); t6.save()
    
    ## Conditions
    
    ## End
    transaction.commit()



def post_syncdb_handler(sender, **kwargs):
    # Create parameters
    if getMyParams().count() == 0:
        setParam(key = u'TOGGLE_MAIL', value = u'OFF', default_value = u'OFF', 
                 description = u'Interrupteur général autorisant ou empéchant tout envoi de mail (ON ou OFF)')
        setParam(key = u'MAIL_FROM', value = u'marc-antoine.gouillart@newarch.fr', 
                 default_value = u'marc-antoine.gouillart@newarch.fr', 
                 description = u'adresse "FROM" des messages émis par l\'application')
    
    # Create default ticket type & workflow if no classes are already defined
    if TicketClass.objects.count() == 0:
        createDefaultTicketClass()
        createDefaultWorkflow()
    
    # Do something else?

## Listen to the syncdb signal
post_syncdb.connect(post_syncdb_handler, sender=models)
