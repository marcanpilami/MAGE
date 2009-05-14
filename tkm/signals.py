# coding: utf-8

## Python imports
import threading

## Django imports 
import django.dispatch


###############################################################################
## Signals   
###############################################################################

modified_field  = django.dispatch.Signal(providing_args = ["FV",])
modified_ticket = django.dispatch.Signal(providing_args = ["ticket",])


class SignalThread(threading.Thread):
    def __init__(self, signal, sender, **kwargs):  
        if not isinstance(signal, django.dispatch.Signal):
            raise TypeException('ce n\'est pas un signal !')
        self.signal = signal  
        self.sender = sender
        self.args = kwargs
        threading.Thread.__init__(self)
        
    def run(self):
        self.signal.send(sender = self.sender, **self.args)