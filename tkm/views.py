# coding: utf-8

"""
    Minimalist Ticket Manager views.
    
    @warning: This is not done, and should no be used. (and is of little interest)
    
    @author: Marc-Antoine Gouillart
    @contact: marsu_pilami@msn.com
    @license: GNU GVL v3
"""

## Django imports
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User, Group, Permission

## Mage imports
from MAGE.tkm.models import *
from MAGE.tkm.forms import build_forms, build_filters


@login_required
def new_ticket(request, ticket_class = u'Ticket de demande d\'intervention'):
    """Création d'un nouveau ticket"""
    return ticket_form(request, ticket_class = ticket_class)

@login_required
def edit_ticket(request, ticket_id):
    """Edition d'un ticket existant"""
    return ticket_form(request, ticket_id = ticket_id)

@transaction.commit_manually
def ticket_form(request, ticket_class = None, ticket_id = None):
    """Création ou mise à jour d'un ticket"""
    if ticket_id:
        tk = Ticket.objects.get(id = ticket_id)
    else: 
        tk = None
    
    ## Get forms
    form_set = build_forms(ticket_class, request = request, ticket = tk)
    
    ## Do something in case of POST
    if request.method == 'POST':
        ## Check validity
        for subform in form_set:
            if not subform.is_valid():
                return render_to_response('tkm_create_ticket.html', {'ticket_forms':form_set, 'ticket':None})
        
        ## Create the ticket itself
        if not ticket_id:
            tk = Ticket(ticket_class = TicketClass.objects.get(name = ticket_class))
            tk.save()
        
        ## Save the field content, add reference to the ticket
        for subform in form_set:
            ## Try and find the old value if it exists
            tfv_old = None
            try: tfv_old = TicketFieldValue.objects.get(ticket = tk, field = TicketField.objects.get(pk = int(subform.prefix))).leaf
            except TicketFieldValue.DoesNotExist: pass
            
            ## Take the new (or unmodified) value from the form
            try:
                tfv = subform.save(commit = False)
            except ValueError:
                continue    ## Optionnal fields that were not completed do not need a TFV object
            
            ## Analyse: has it changed?
            if tfv_old and tfv_old.value != tfv.value:
                ## It has changed!
                ## Save the TFV
                tfv.save()
            
            if not tfv_old:
                ## It is new!
                ## Complete the TFV
                tfv.ticket = tk
                tfv.field = TicketField.objects.get(pk = int(subform.prefix))
            
                ## Save the TFV
                tfv.save()
        
        ## End transaction and redirect
        transaction.commit()
        return HttpResponseRedirect(reverse('MAGE.tkm.views.summary'))
             
    ## Return void form if not POST
    return render_to_response('tkm_create_ticket.html', {'ticket_forms':form_set, 'ticket':tk}, context_instance=RequestContext(request))


def summary(request, summary_name = u'Rapport par défaut'):
    """Vue synthétique des tickets"""
    summary = TabularSummary.objects.get(name = summary_name)
     
    ## Build filter block
    form_set = build_filters(request)
    
    
    ## Filter
    ticket_set = None
    if request.method == 'POST':
        for subform in form_set:
            if not subform.is_valid():
                continue # An invalid form should not lead to a filter !
            
            if not subform.cleaned_data['value']:
                continue # Pass void fields
            
            tmp = [tck for tck in Ticket.objects.search(subform.cleaned_data['value']).all()]
            #raise Exception('meuh')
            if not ticket_set:
                ticket_set = tmp
            else:
                for tck in ticket_set:     ## Don't use the QuerySet &, it simply can't work (combining INNER JOIN = FAIL)... 
                    if not tmp.__contains__(tck):
                        ticket_set.remove(tck)
    else:
        ticket_set = Ticket.objects.all()
    
    ## Build data lists    
    blocks = [bl for bl in summary.blocks.all()]
    for bl in blocks:
        bl.ticket_data = []
        for tt in ticket_set:
            tk_data = []
            for f in bl.fields.all():
                try:
                    ff = tt.field_values.get(field = f)
                except TicketFieldValue.DoesNotExist:
                    ff = None
                tk_data.append(ff)
            bl.ticket_data.append((tt, tk_data))         
        
    return render_to_response('tkm_view_summary.html', 
                              { 'summary':summary, 
                                'tickets':ticket_set, 
                                'blocks':blocks,
                                'form_set':form_set},
                              context_instance=RequestContext(request))




#####################################################################################
## Permissions
#####################################################################################

class PermissionForm(ModelForm):
    class Meta:
        model = FieldPermissions
        fields = ('can_read', 'can_alter',)

def set_permissions(request, ticket_class = u'Ticket de demande d\'intervention'):
    """Gestion des habilitations TKM"""
    tc = TicketClass.objects.get(name = ticket_class)
    
    ## Liste des groupes
    grs = Group.objects.all()
    
    ## Liste des champs...
    fields = tc.fields.select_related().all()
    for f in fields:
        f.perms = []
        f.subforms = []
        for gr in grs:
            fp = f.get_or_create_permission(gr)
            f.perms.append(fp)
            
            form_args = {'instance':fp, 'prefix':fp.pk}
            if request and request.method == 'POST':
                form_args['data'] = request.POST
            form = PermissionForm(**form_args)
            f.subforms.append(form)
    
    ## Save data if necessary
    if request and request.method == 'POST':
        for f in fields:
            for form in f.subforms:
                if form.has_changed():
                    form.save()
        
    ## End
    return render_to_response('tkm_perms.html', {'fields':fields, 'groups':grs})
    
