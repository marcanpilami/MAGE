from scm.models import Play,Task,Attribute
from django.utils.encoding  import  * 
from django.forms.models import BaseInlineFormSet
from django.forms.models import inlineformset_factory
from django.forms.models import *
from django.shortcuts import  get_object_or_404, render, redirect,render_to_response
from django.db import models
from django.db.models  import fields
from django.forms import *
from django import  forms
from ref.models.description import ImplementationDescription,ImplementationFieldDescription, \
    ImplementationComputedFieldDescription


import os

from django.forms import ModelForm    
from scm.models import Play,Task,Attribute
from scm.views import generate_the_playbook

"""SAMPLE_CHOICES_LIST = (('>=', '>='),
                        ('<=', '<='),
                        ('==', '==')) """



#AttributeFormset =None

def formfield_callback(field):
    if isinstance(field, fields.CharField) and field.name == 'mannuel_value':
        print ('entree') 
        
        return fields.CharField(choices = SAMPLE_CHOICES_LIST,label='Sample Label')
    
    return field.formfield()



#TaskFormset = inlineformset_factory(Play, Task, extra=1)
"""AttributeFormset = inlineformset_factory(Task, Attribute, extra=0,fields=('name','mannuel_value',),widgets={
    
    'name': Textarea(attrs={'cols': 5, 'rows': 1},),
    'mannuel_value': Select(attrs={'cols': 5, 'rows': 1},choices=SAMPLE_CHOICES_LIST ),
   
    
})"""




class BaseTaskFormset(BaseInlineFormSet):
       def add_fields(self, form, index):
        super(BaseTaskFormset, self).add_fields(form, index) 
         # save the formset in the 'nested' property
        form.nested = AttributeFormset(
                        instance=form.instance,
                        data=form.data if form.is_bound else None,
                        files=form.files if form.is_bound else None,
                        prefix='attributes-%s-%s' % (
                            form.prefix,
                            AttributeFormset.get_default_prefix())
                        )
       
      
       
       def is_valid(self):
        result = super(BaseTaskFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()

        return result
    
       def save(self, commit=True):

         result = super(BaseTaskFormset, self).save(commit=commit)

         for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

         return result
    
       

"""TaskFormset = inlineformset_factory(Play,
                                        Task,
                                        formset=BaseTaskFormset,
                                        extra=1,exclude=())"""




def manage_task(request, play_id):
    #global SAMPLE_CHOICES_LIST    # Needed to modify global copy of globvar
   
    

    
    print('#############################################')
    #print (SAMPLE_CHOICES_LIST)
    """Edit children and their addresses for a single parent."""

    play = get_object_or_404(Play, id=play_id)

    if request.method == 'POST':
        
        
        formset = TaskFormset(request.POST, instance=play)
        if formset.is_valid():
            formset.save()
            print ('saved succefully')
            #return redirect('parent_view', parent_id=parent.id)
            
            #generating the playbook 
            generate_the_playbook(play_id)
            
            
            
            
            
            return redirect('scm:ansible2') 
            #return  redirect('welcome')
    else:
        
        
        global SAMPLE_CHOICES_LIST
        SAMPLE_CHOICES_LIST =((None, '----------'),
                        ('1', '1111'),
                        ('2', '2'),
                        ('45', '45'))
        
        #extraction de la description name 
        hosts=play.hosts
        description_list=hosts.split(',')
        desciption_name=description_list[0][1:]
        target_ugly=description_list[1]
        
        target=target_ugly[:(len(target_ugly)-1)]
        
        
        
        #description_na =desciption_name.encode('utf8')
        
        #description_na= smart_bytes(desciption_name, encoding='utf-8', strings_only=False, errors='strict')
       
        description_na=str(desciption_name)
        target_name=str(target)
        
        
        print desciption_name
        print type(desciption_name)
        print type(description_na)
       
        
        print  description_na[2:(len(description_na)-1)]
        description_na=description_na[2:(len(description_na)-1)]
        target_name=target_name[2:(len(target_name)-1)]
        
        print 'the target name is '+ target_name
        
        
        print 'hello'
        print 'the description name is '+description_na
        print 'the target  is '+target
        if desciption_name=='9500':
            print 'no specific description for a logical component '
            SAMPLE_CHOICES_LIST=((None, '----------'),)
        else :
            description = get_object_or_404(ImplementationDescription, name=description_na)
            description_nn=description.name
            print 'the name from the database'+description_nn
            SAMPLE_CHOICES_LIST=creating_choice_list(description_nn)
           
            print 'the sample choices list is '+ str(SAMPLE_CHOICES_LIST)
       
        
        
        print description_list
        
        
        
        #SAMPLE_CHOICES_LIST=creating_choice_list('osserver')
        #print (creating_choice_list('osserver'))
        global AttributeFormset
        AttributeFormset = inlineformset_factory(Task, Attribute, extra=2,fields=('name','mannuel_value','automatique_value',),widgets={
    
              
            
              
               'automatique_value': Select(attrs={'cols': 5, 'rows': 1,'required': False},choices=SAMPLE_CHOICES_LIST ),
             })
        
        
        
        global TaskFormset
        TaskFormset = inlineformset_factory(Play,
                                        Task,
                                        formset=BaseTaskFormset,
                                        extra=2,exclude=(),widgets={
    
              
            
              'delegate_to': Select(attrs={'cols': 5, 'rows': 1,'required': False},choices=SAMPLE_CHOICES_LIST ),
   
    
             })
        #global AttributeFormset      
        print 'the name of the play'
        print play.name
        formset = TaskFormset(instance=play)
        """for form in formset:
            print (type(form))
            if isinstance(form, fields.CharField) and form.name == 'mannuel_value':
                     print ('yeeeeee########################################s') 
            for formfield in form :
                
                if formfield.name=='module_name':
                    formfield=  forms.MultipleChoiceField(
                                            required=False,
                                            widget=forms.CheckboxSelectMultiple,
                                            choices=SAMPLE_CHOICES_LIST,
                                        )
                    
                    
                    print 'good'
                
                
                print form.prefix"""            
        
    return render(request, 'scm/ansible_part1.html', {
                  'play':play,
                  'task_formset':formset})



    
def creating_choice_list(description_name): 
    
 #SAMPLE_CHOICES_LIST=()
    #filter(pk=description_id)
 descriptions = ImplementationDescription.objects.\
                    prefetch_related('field_set','computed_field_set','target_set__link_type','relationships').filter(name=description_name).distinct()
    
 for description in descriptions:
    SAMPLE_CHOICES_LIST=((None, '----------'),)
    
    print description.name 
    #extraction des valeurs simples 
    for v in description.field_set.all():
          SAMPLE_CHOICES_LIST= SAMPLE_CHOICES_LIST +((v.name.replace(" ","-"),v.name),) 
    
    
    #extraction des valeurs calculs 
    for v in description.computed_field_set.all():
          SAMPLE_CHOICES_LIST= SAMPLE_CHOICES_LIST +((v.name.replace(" ","-"),v.name),)                 
    
    
    #extraction des ralations 
    for v in description.relationships.all():
          SAMPLE_CHOICES_LIST= SAMPLE_CHOICES_LIST +((v.name.replace(" ","-"),v.name),)
    
    
       
    
    
    return  SAMPLE_CHOICES_LIST
 
 
 
 
 
 class PlayForm(ModelForm):
      class Meta:
         model = Play
         fields = ['name', 'hosts', 'strategy']
 
 
 
 
 

