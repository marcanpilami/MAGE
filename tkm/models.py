# coding: utf-8

###############################################################################
##
## Minimalist ticket manager
##    
###############################################################################

## Python imports
import threading

## Django imports
from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q
import django.dispatch


## MAGE imports
from MAGE.ref.models import Component, Environment
from signals import *
import mail # will init signal listening


###############################################################################
## Base models      
###############################################################################

#########################
## Ticket Field     
#########################

class FieldPermissions(models.Model):
    group = models.ForeignKey(Group)
    field = models.ForeignKey('TicketField')
    
    can_read = models.BooleanField(verbose_name = u'Voir', default = True)
    can_alter = models.BooleanField(verbose_name = u'Modifier', default = False)

class FieldPermissionsInline(admin.TabularInline):
    model = FieldPermissions
    extra = 3

class TicketField(models.Model):
    """Ticket Field. Polymorphic model, leaf is the child object"""
    name = models.CharField(max_length = 50, verbose_name=u'Nom du champ (affiché dans les formulaires)')
    description = models.TextField(verbose_name=u'Description de l\'utilité du champ (affiché dans les tooltips)')
    compulsory = models.BooleanField(verbose_name = u'Ce champ est-il obligatoire ?', default=True)
    valued_by = None
    default = None
    
    ## Permissions
    groups = models.ManyToManyField(Group, through = FieldPermissions, verbose_name = 'autorisations associées au champ')
    def get_or_create_permission(self, group):
        try:
            return self.fieldpermissions_set.get(group = group)
        except FieldPermissions.DoesNotExist:
            tmp = FieldPermissions(group = group, field = self)
            tmp.save()
            return tmp
    
    ## Polymporphism handling
    final_type = models.ForeignKey(ContentType, editable = False) 
    def save(self, *args, **kwargs) :
        self.final_type = ContentType.objects.get_for_model(type(self))
        super(TicketField, self).save(*args, **kwargs) 
    def _getLeaf(self):
        return self.final_type.get_object_for_this_type(id=self.id) 
    leaf = property(_getLeaf)
    
    ## Str for forms (admin)
    def __unicode__(self):
        return u'%s' %self.name
    
    class Meta:
        ordering = ['name',]

class TicketFieldAdmin(admin.ModelAdmin):
    list_display = ['name','description','compulsory',] 
    inlines = [FieldPermissionsInline, ]
    
class TicketFieldInline(admin.TabularInline):
    model = TicketField
    extra = 1

#TODO: use a through M2M here ?
class TicketFieldValue(models.Model):
    last_update_date = models.DateTimeField(auto_now = True, verbose_name = u'date de dernière mise à jour')
    ticket = models.ForeignKey('Ticket', related_name = 'field_values', editable = False)
    field = models.ForeignKey('TicketField', editable = False, verbose_name = u'champ valué')
    value = None
    
    def value_restriction(self):
        try:
            return self.field.leaf.choices
        except AttributeError:
            return None
    choices = property(value_restriction)
    
    ## Polymporphism handling
    final_type = models.ForeignKey(ContentType, editable = False) 
    def save(self, *args, **kwargs) :
        self.final_type = ContentType.objects.get_for_model(type(self))
        super(TicketFieldValue, self).save(*args, **kwargs) 
        #modified_field.send(sender = self, FV = self)
        SignalThread(signal = modified_field, sender = self, FV = self).start()
    def _getLeaf(self):
        return self.final_type.get_object_for_this_type(id=self.id) 
    leaf = property(_getLeaf)
    
    class Meta:
        verbose_name = u'valeur du champ (debug)'
        verbose_name_plural = u'valeurs des champs (debug)'
    
    def __unicode__(self):
        return self.leaf.value
    
    def getFullText(self):
        return "%s :\n%s" %(self.field.name, self.leaf.__unicode__())
    
#TODO: debug only
class TicketFieldValueAdmin(admin.ModelAdmin):
    list_display = ['ticket','field','__unicode__',] 
 

#########################
## Ticket classes      
#########################

class FieldDisposition(models.Model):
    ticket_class = models.ForeignKey('TicketClass', related_name='field_dispositions')
    field = models.ForeignKey(TicketField, verbose_name = u"champ à afficher")
    group = models.CharField(max_length = 50, verbose_name = u"groupe", default = u'groupe par défaut')
    position = models.IntegerField(max_length = 2, verbose_name = u"position dans le groupe", default = 1)
    cr = models.BooleanField(verbose_name = u'Forcer un retour à la ligne', default = False)
    class Meta:
        ordering = ['group', 'position',]
        verbose_name = u"Disposition d'un champ"
        verbose_name_plural = u"Disposition des champs"
    def __unicode__(self):
        return u"disposition du champ %s dans %s" %(self.field.name.lower(), self.ticket_class.name.lower())

class FieldDispositionInline(admin.TabularInline):
    model = FieldDisposition
    extra = 10
    
class TicketClass(models.Model):
    """Class of tickets, ie. description of a ticket type. Does not store any fields values !"""
    name = models.CharField(max_length = 50, verbose_name = u'Nom de la classe de tickets')
    fields = models.ManyToManyField(TicketField, verbose_name = u'Champs ', through = FieldDisposition)
    
    class Meta:
        verbose_name = u'type de tickets'
        verbose_name_plural = u'types de tickets'

    def __unicode__(self):
        return u'%s' %self.name
    
class TicketClassAdmin(admin.ModelAdmin):
    list_display = ['name',]
    inlines = [FieldDispositionInline, ]


class TicketManager(models.Manager):
    def search(self, *values):
        res = None
        ct = ContentType.objects.filter(ticketfieldvalue__pk__isnull = False).distinct()
        
        for val in values:
            q_val = None
            for content_type in ct:
                TFV = content_type.model_class()
                
                ## Get model true name
                model_attribute_name = TFV._meta.object_name.lower()
                if model_attribute_name == 'ticketfieldvalue': continue ## No need to query the base object 
                
                ## Check compatibility between val and the field
                field_value_model = TFV.objects.all()[0].value.__class__## Dirty hack. But how else could we retrieve this ?
                if not isinstance(val, field_value_model): continue     ## No need to make a stupid query
                
                ## Create filter, using inheritance
                parent = TFV._meta.parents.keys()[0]                    ## multiple inheritance is not supported
                filter = model_attribute_name
                while parent._meta.object_name.lower() != 'ticketfieldvalue': 
                    tmp_name = parent._meta.object_name.lower()
                    filter = tmp_name + '__' + filter
                    parent = parent._meta.parents.keys()[0]
                filter = 'field_values__' + filter + '__value' 
                f = {filter:val}
                print f
                
                ## Restrict queryset using filter
                tmp = Q(**f)
                tmp = tmp | tmp
                #tmp.connector=tmp.OR ## to avoid any INNER JOIN, as we prefer LEFT JOIN
                if q_val:                  
                    q_val = q_val | tmp
                else:
                    q_val = tmp
            if res:
                res = (res) & (q_val)
                print 'surcharge avec %s donne : %s' %(q_val, res)
                print self.filter(res).all()
            else:
                res = q_val
                print 'init %s' %res
                print self.filter(res).all()     
            
            print res.__class__   
                
        #if res: print res.query
        print self.filter(res).query
        #if res: return self.filter(res).distinct()
        return res
    
class Ticket(models.Model):
    """Instance de ticket, avec toutes ses valeurs"""
    id = models.AutoField(verbose_name = u'numéro du ticket', primary_key = True)
    creation_date = models.DateTimeField(auto_now_add = True, verbose_name = u'Date de création')
    last_update_date = models.DateTimeField(auto_now = True, verbose_name = u'Date de dernière mise à jour')
    ticket_class = models.ForeignKey(TicketClass, verbose_name = u'Type de ticket', editable = False)
    
    watchers = models.ManyToManyField(User, verbose_name = u'personnes suivant ce ticket', null=True, blank=True, related_name = 'tickets_watched')
    reporter = models.ForeignKey(User, verbose_name = u'créateur du ticket', blank=True, null = True, related_name = 'tickets_created')
    
    objects = TicketManager()
    
    def __unicode__(self):
        return u"%s" %self.id
    
    def getFullText(self):
        res = u'Ticket n°%s\n\n' %self.id
        for tfv in self.field_values.all():
            res += tfv.getFullText()+ u"\n\n"
        return res
    
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id','last_update_date', 'creation_date', ]
    ordering = ['last_update_date']
    search_fields = ['id',]# 'field_values__leaf__value',]



###############################################################################
## Fields      
###############################################################################

#########################
## Lists      
#########################

class ListElement(models.Model):
    """List member. One element belongs to only one list."""
    elt = models.CharField(max_length=50, verbose_name=u'élément de liste')
    level = models.IntegerField(max_length=5, verbose_name='Poids relatif de l\'élément', blank=True, null=True)
    parent_list = models.ForeignKey('TF_List', 
                                    related_name='choices', 
                                    verbose_name = u'liste à laquelle cet élément appartient')
    default = models.BooleanField(default = False, verbose_name = u'est-ce la valeur par défaut ?')
    
    def __unicode__(self):
        return u'%s' %self.elt
    
    class Meta:
        verbose_name=u'élément de liste de choix'
        verbose_name_plural=u'éléments de liste de choix'
        ordering = ['level',]
    

class TFV_List(TicketFieldValue):
    value = models.ForeignKey(ListElement)
    def __unicode__(self):
        return self.value.elt

class TF_List(TicketField):
    class Meta:
        verbose_name=u'liste de choix'
        verbose_name_plural=u'listes de choix'
    valued_by = TFV_List
    def _getDefault(self):
        try: return self.choices.get(default=True).pk
        except: return None
    default = property(_getDefault)

class ListElementInline(admin.TabularInline):
    model = ListElement
    extra = 3
    
class TF_admin_List(admin.ModelAdmin):
    list_display = ['name','description','compulsory']
    inlines = [ListElementInline, ]
    
    

#########################
## Envt list      
#########################
 
class TFV_Envt(TicketFieldValue):
    value = models.ForeignKey(Environment, related_name='ticket_fields')
    def __unicode__(self):
        return self.value.name

class TF_EnvtList(TicketField):
    valued_by = TFV_Envt



#########################
## User list      
#########################
 
class TFV_User(TicketFieldValue):
    value = models.ForeignKey(User, related_name='ticket_fields')
    def __unicode__(self):
        return self.value.__unicode__()

class TF_User(TicketField):
    valued_by = TFV_User



#########################
## Group list      
#########################
 
class TFV_Group(TicketFieldValue):
    value = models.ForeignKey(Group, related_name='ticket_fields')
    def __unicode__(self):
        return self.value.__unicode__()
    
class TF_Group(TicketField):
    valued_by = TFV_Group
    


#########################
## Free Text Fields
#########################
 
class TFV_Text(TicketFieldValue):
    value = models.TextField()
    
class TF_Text(TicketField):
    valued_by = TFV_Text
    class Meta:
        verbose_name=u'Champ texte libre'
        verbose_name_plural=u'Champs texte libre'

class TFV_ShortText(TicketFieldValue):
    value = models.CharField(max_length = 200)
    
class TF_ShortText(TicketField):
    valued_by = TFV_ShortText
    class Meta:
        verbose_name=u'Champ texte court'
        verbose_name_plural=u'Champs texte court'



###############################################################################
## Summary      
###############################################################################

class SummaryBlock(models.Model):
    BLOCK_TYPE = ((1, u'Block'), (2, u'Tab'))
    summary = models.ForeignKey('TabularSummary', related_name = 'blocks')
    fields = models.ManyToManyField(TicketField, verbose_name = u'Champs à afficher')
    type = models.IntegerField(max_length = 2, choices = BLOCK_TYPE, verbose_name = u'Comment afficher ce bloc', default = 2)

    class Meta:
        verbose_name = u'Bloc de données'
        verbose_name_plural = u'Blocs de données'
        
class SummaryBlockInline(admin.TabularInline):
    model = SummaryBlock
    extra = 1

class TabularSummary(models.Model):
    name = models.CharField(max_length = 200, verbose_name = u'Nom du rapport')
    
    class Meta:
        verbose_name = u'page de résumé'
        verbose_name_plural = u'pages de résumé'
        ordering = ['name', ]
    def __unicode__(self):
        return self.name

class SummaryAdmin(admin.ModelAdmin):
    inlines = [SummaryBlockInline, ]



###############################################################################
## Workflow      
###############################################################################

class State(models.Model):
    """A state in a workflow. I.e., a list element"""
    name = models.CharField(max_length=50, verbose_name=u'nom de l\'état')
    allowed_states = models.ManyToManyField('State', 
                                            through = 'Transition', 
                                            verbose_name = u'Etats pouvant succéder à cet état',
                                            related_name = 'preceding_states',
                                            symmetrical = False)
    
    level = models.IntegerField(max_length=5, verbose_name='Poids relatif de l\'élément', blank=True, null=True)
    workflow = models.ForeignKey('Workflow', 
                                    related_name='choices', 
                                    verbose_name = u'workflow auquel cet état appartient')
    start = models.BooleanField(default = False, verbose_name = u'état de départ ?')
    
    def __unicode__(self):
        return u'%s' %self.name
    
    class Meta:
        verbose_name = u'état de cheminement de travail'
        verbose_name_plural = u'états de cheminement de travail'
        ordering = ['level',]

class StateValue(TicketFieldValue):
    value = models.ForeignKey(State)
    
    def save(self, *args, **kwargs):
        """to be overloaded"""
        super(StateValue, self).save(*args, **kwargs)
        
    def next_value_restriction(self, user):
        res = []
        for transition in self.value.transitions_out.all():
            if transition.is_possible(self.ticket, user): res.append(transition.target_state.pk)
        if self.leaf.value.pk not in res: res.append(self.leaf.value.pk)
        
        ## Hack to return a RS instead of a list...
        return State.objects.filter(pk__in = res)
    choices = property(next_value_restriction) 
                
class Transition(models.Model):
    target_state = models.ForeignKey(State, related_name = 'transitions_in', verbose_name = u'état cible')
    source_state = models.ForeignKey(State, related_name = 'transitions_out', verbose_name = u'état source')
    comment = models.TextField(verbose_name = u'description de cette transition, de ses conditions...')
    authorised_groups = models.ManyToManyField(Group, verbose_name = u'groupes autorisés à effectuer cette transition')
    
    def is_possible(self, ticket, user):
        """@return: True if the transition is possible within the given ticket """    
        ## User permission test
        if user.groups.select(pk__in=authorised_groups.values['pk']).count() == 0:
            return false    ## The user is not in any group authorized to do this transition
        
        ## Condition check
        for cond in self.conditions.all():
            if not cond.is_verified(ticket): return False
        
        ## If here, the user and the ticket are OK for the transition
        return True
    
    def __getWK(self):
        return self.target_state.parent_list.leaf
    workflow = property(__getWK)
    def __unicode__(self):
        return u'%s : de "%s" à "%s"' %(self.workflow, self.source_state.elt, self.target_state.elt)
    
    class Meta:
        verbose_name = u'transition conditionnelle'
        verbose_name_plural = u'transitions conditionnelles'

   
class Workflow(TF_List):
    valued_by = StateValue
    creator_can_close = models.BooleanField(verbose_name = u'le créateur d\'un ticket peut le fermer')
    
    def _getDefault(self):
        try: return self.choices.get(start=True).pk
        except: return None
    default = property(_getDefault)
    
    class Meta:
        verbose_name = u'cheminement de travail'
        verbose_name_plural = u'cheminements de travail'

        
class Condition(models.Model):
    target_field = models.ForeignKey(TF_List, verbose_name = u'champ sur lequel porte la condition')
    min_weight = models.IntegerField(max_length = 3, verbose_name = u'poids minimum pour réussir la condition')
    transition = models.ForeignKey(Transition, related_name = 'conditions', verbose_name = 'transition sur laquelle porte la condition')
    
    class Meta:
        verbose_name = u'Condition de transition (garde) d\'un état vers un autre'
        verbose_name = u'Conditions de transition (garde) d\'un état vers un autre'
    
    def is_verified(self, ticket):
        try:
            ticket.field_values.filter(field = self.target_field).filter(value__level__ge=self.min_weight)
        except:
            return False
        return True


class ConditionInline(admin.TabularInline):
    model = Condition
class TransitionInline(admin.TabularInline):
    model = Transition
    extra = 1
    fk_name = "source_state"

class TransitionAdmin(admin.ModelAdmin):
    list_display = ['__unicode__',]
    inlines = [ConditionInline,]

class StateAdmin(admin.ModelAdmin):
    inlines = [TransitionInline, ]
    list_display = ['workflow', 'name',]       
    
class StateInline(admin.TabularInline):
    model = State
    extra = 3
    inlines = [TransitionInline,]     

class WorkflowAdmin(admin.ModelAdmin):
    inlines = [StateInline,]    
        
        
        
###############################################################################
## Admin registrations      
###############################################################################
 
admin.site.register(TicketClass, TicketClassAdmin)
admin.site.register(TF_List, TF_admin_List)
admin.site.register(TF_Text, TicketFieldAdmin)
admin.site.register(TF_ShortText, TicketFieldAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TabularSummary, SummaryAdmin)
admin.site.register(TicketFieldValue, TicketFieldValueAdmin)

admin.site.register(Workflow, WorkflowAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Transition, TransitionAdmin)
