# encoding: UTF-8

"""
    Ticket Link API provider
    
    No models here : tickets are not supposed to be stored in MAGE.
    This is just an API, giving base classes
    
    @author: MAG
    @license: GNU GPL v
"""


#from django.db import models

# Create your models here.


class Ticket():
    def __init__(self, id, title, description, reporter, assigned_to):
        self.id = id
        self.title = title
        self.description = description
        self.reporter = reporter
        self.assigned_to = assigned_to
        
    def flush(self):
        raise NotImplementException('flush')
    
    def update(self):
        raise NotImplementedException('update')
        