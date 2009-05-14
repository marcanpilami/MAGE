# coding: utf-8

## Django imports
from django.forms import ModelForm, Form
from django import forms
from django.forms.widgets import Select

## MAGE imports
from MAGE.tkm.models import *


#TODO: default ticket class should be a parameter
def build_forms(ticket_class = u'Ticket de demande d\'intervention', request = None, ticket = None):
    """
        @param ticket_class: ignored if a ticket is specified
        @param request: fill the form with data from this request
        @param ticket: fill the form with data from this ticket, and bound the form to this ticket.  
    """
    ## Retrieve the ticket descriptor
    if ticket:
        ticket_class = ticket.ticket_class
    else:
        ticket_class = TicketClass.objects.get(name = ticket_class)
    
    ## User
    if request and request.user:
        user = request.user
    else: 
        user = None
    
    ## Build the forms from the descriptor
    form_set = []
    for field_disposition in ticket_class.field_dispositions.all():
        cast_field = field_disposition.field.leaf
        
        ## Check that the user is allowed to see the field
        dis = False
        mod = False
        if user:    
            for gr in user.groups.all():
                perm = cast_field.get_or_create_permission(gr)
                if perm.can_read: dis = True;break
                if perm.can_alter: mod = True; break
            if not dis: continue
        
        ## Build form for the field, bind it if necessary 
        class GenericFieldForm(ModelForm):
            class Meta:
                model = cast_field.valued_by
        
        kwargs = {'prefix':cast_field.pk,}
        if request != None and request.method == 'POST':
            kwargs['data'] = request.POST
            kwargs['files'] = request.FILES
        if ticket:
            try:
                kwargs['instance'] = ticket.field_values.get(field = cast_field).leaf
            except TicketFieldValue.DoesNotExist:
                pass ## All fields are not compulsory, so their TFV may not exist
        form = GenericFieldForm(**kwargs)
        
        ## Field customisation    
        value_field = form.fields['value']
        value_field.label = cast_field.name
        value_field.required = cast_field.compulsory
        value_field.initial = cast_field.default
        ## In some cases, the choice queryset must be restricted (by developper choice or due to workflow constraints)
        try:
            value_field.queryset = cast_field.choices.all()
        except:
            pass
        if ticket:
            try:
                choices = ticket.field_values.get(field = cast_field).leaf.choices
                if choices:  value_field.queryset = choices.all()
            except TicketFieldValue.DoesNotExist:
                pass ## All fields are not compulsory, so their TFV may not exist
   
        ## Add a reference to the presentation options to the form
        form.prez = field_disposition
        
        ## Add the formset to the list
        form_set.append(form)
        
    return form_set


def build_filters(request = None):
    form_set = []
    
    ## Take all forms taht can be created from the ticket class and filter them.
    for form in build_forms(request = request):
        if form.fields['value'].widget.__class__ == Select:
            form_set.append(form)
            form.fields['value'].initial = None
            form.fields['value'].required = False
    
    ## Add a search form
#    if request and request.method == 'POST':
#        tmp = SearchForm(request, prefix = 'search')
#    else:
#        tmp = SearchForm(prefix = 'search')
#    form_set.append(tmp)
    
    ## Return the forms
    return form_set

class SearchForm(forms.Form):
    value = forms.CharField(max_length = 200, label='Recherche plein texte ', required = False)