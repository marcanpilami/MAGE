# coding: utf-8

import codecs
import sys
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ref.models import ComponentInstance, CI2DO, Project, Application, EnvironmentType , LogicalComponent, ComponentImplementationClass, Environment

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

class Command(BaseCommand):
    help = 'displays SQL commands to go from MAGE 5 to MAGE 6'
    args = ''
    
    def handle(self, *args, **options):
    
        cif_id=0
        ci_e_id=0
        
        for p in Project.objects.all():
            print u"INSERT INTO ref_project(id, name, alternate_name_1, alternate_name_2, alternate_name_3, description) VALUES(%s, '%s', %s, %s, %s, '%s');" %(p.pk, p.name, "'" + p.alternate_name_1 + "'" if p.alternate_name_1 else 'NULL', "'" + p.alternate_name_2 + "'" if p.alternate_name_2 else 'NULL', "'" + p.alternate_name_3 + "'" if p.alternate_name_3 else 'NULL', p.description.replace("'", "''"))
        
        for p in Application.objects.all():
            print u"INSERT INTO ref_application(id, name, alternate_name_1, alternate_name_2, alternate_name_3, description, project_id) VALUES(%s, '%s', %s, %s, %s, '%s', %s);" %(p.pk, p.name, "'" + p.alternate_name_1 + "'" if p.alternate_name_1 else 'NULL', "'" + p.alternate_name_2 + "'" if p.alternate_name_2 else 'NULL', "'" + p.alternate_name_3 + "'" if p.alternate_name_3 else 'NULL', p.description.replace("'", "''"), 'NULL' if not p.project else p.project_id)
        
        for lc in LogicalComponent.objects.all():
            print u"INSERT INTO REF_LOGICALCOMPONENT(ID, NAME, DESCRIPTION, APPLICATION_ID, SCM_TRACKABLE, ACTIVE, REF1, REF2, REF3) VALUES(%s, '%s', '%s', %s, %s, %s, %s, %s, %s);" %(lc.pk, lc.name, lc.description.replace("'", "''"), lc.application_id, 1 if lc.scm_trackable else 0, 1 if lc.active else 0, "'" + lc.ref1 + "'" if lc.ref1 else "NULL", "'" + lc.ref2 + "'" if lc.ref2 else "NULL", "'" + lc.ref3 + "'" if lc.ref3 else "NULL")
        
        for cic in ComponentImplementationClass.objects.all():
            print u"INSERT INTO ref_componentimplementationclass(ID, NAME, DESCRIPTION, IMPLEMENTS_ID, SLA_ID, TECHNICAL_DESCRIPTION_ID, REF1, REF2, REF3, ACTIVE) VALUES(%s, '%s', '%s', %s, NULL, %s, %s, %s, %s, %s);" %(cic.pk, cic.name, cic.description.replace("'", "''"), cic.implements_id, "(SELECT ID FROM ref_implementationdescription WHERE lower(NAME)=lower('%s'))" %cic.python_model_to_use.model, "'" + lc.ref1 + "'" if lc.ref1 else "NULL", "'" + lc.ref2 + "'" if lc.ref2 else "NULL", "'" + lc.ref3 + "'" if lc.ref3 else "NULL", 1 if cic.active else 0)
        
        for t in EnvironmentType .objects.all():
            print "INSERT INTO ref_EnvironmentType(id, name, description, short_name, chronological_order, default_show_sensitive_data) VALUES(%s, '%s', '%s', '%s', %s, %s);" %(t.pk, t.name, t.description.replace("'", "''"), t.short_name, t.chronological_order, 1 if t.default_show_sensitive_data else 0)
            
            for cic in t.implementation_patterns.all():
                print u"INSERT INTO ref_environmenttype_implementation_patterns (environmenttype_id, componentimplementationclass_id) VALUES(%s, %s);" %(t.id, cic.id)            
        
        for e in Environment.objects.all():
            print u"INSERT INTO REF_ENVIRONMENT(ID, name, builddate, destructiondate, description, manager, project_id, typology_id, template_only, active, show_sensitive_data, managed) VALUES(%s, '%s', date(%s, 'unixepoch'), %s, '%s', '%s', %s, %s, %s, %s, %s, %s);" %(
                    e.pk, 
                    e.name,  
                    (e.buildDate - datetime.date(1970,1,1)).total_seconds(), 
                    "NULL" if not e.destructionDate else "date(%s, 'unixepoch')" %((e.destructionDate - datetime.date(1970,1,1)).total_seconds(),), 
                    e.description.replace("'", "''"), 
                    e.manager, 
                    e.project_id, 
                    e.typology_id, 
                    1 if e.template_only else 0, 
                    1 if e.active else 0, 
                    (1 if e.show_sensitive_data else 0) if e.show_sensitive_data != None else "NULL", 
                    1 if e.managed else 0)       
        
        for ci in ComponentInstance.objects.all():
            print "INSERT INTO ref_ComponentInstance(id, instanciates_id, description_id, deleted, include_in_envt_backup) values(%s, %s, (SELECT ID from ref_ImplementationDescription WHERE name='%s'), %s, %s);" %(ci.pk, ci.instanciates_id if ci.instanciates_id else "NULL", ci.model.model, 1 if ci.deleted else 0, 1 if ci.include_in_envt_backup else 0)
            
            for e in ci.environments.all():
                print "INSERT INTO ref_componentinstance_environments(ID, componentinstance_id, environment_id) VALUES(%s, %s, %s);" %(ci_e_id, ci.pk, e.pk)
                ci_e_id+=1
            
            for field in ci.leaf._meta.fields:
                if field.column in ('id', 'include_in_envt_backup', 'deleted', 'instanciates_id', 'model_id', 'componentinstance_ptr_id'):
                    continue
                    
                print "INSERT INTO ref_ComponentInstanceField(id, value, field_id, instance_id) VALUES(%s, '%s', (SELECT fd.ID from ref_ImplementationFieldDescription fd LEFT JOIN ref_ImplementationDescription d ON fd.description_id = d.id WHERE fd.name='%s' AND d.name='%s'), '%s');" %(cif_id, field.value_to_string(ci.leaf), field.column, ci.model.model, ci.pk)
                
                cif_id+=1
                
        for c in CI2DO.objects.all():
            print "INSERT INTO ref_componentinstancerelation(id, source_id, target_id, field_id) VALUES(%s, %s, %s, (SELECT fd.ID from ref_ImplementationRelationDescription fd LEFT JOIN ref_ImplementationDescription d ON fd.source_id = d.id WHERE fd.name='%s' AND d.name='%s'));" %(c.pk, c.statue_id, c.pedestal_id, c.rel_name, c.statue.model.model)
        
        
            