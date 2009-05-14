# coding: utf-8

## Python imports
import threading 

## Django imports
from django.db.models.signals import post_syncdb
from django.db import transaction
from django.core.mail import send_mail

## MAGE imports
from signals import modified_field


def build_recipient_list(ticket):
    ## People who have chosen to listen to all creation events
    
    ## People who monitor the ticket
    
    ## Author of the ticket
    
    ## Members of the same groups as the author
    
    ## Handler of the ticket
    
    ## Members of the same groups as the author
    
    ## People who have modified the ticket in the past, not already included in the list
    
    return ['mag@newarch.fr',]

def new_ticket_event_handler():
    pass
  

def modified_field_event_handler(sender, **kwargs):
    ticket = kwargs['FV'].ticket
    recipients = build_recipient_list(ticket)
    send_mail('Ticket %s modifié' %ticket.pk, 
              ticket.getFullText(), 
              'marc-antoine.gouillart@newarch.fr', 
              recipients)
    


modified_field.connect(modified_field_event_handler)
