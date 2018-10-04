# coding: utf-8
from ref.models import Environment,Project,LogicalComponent,ComponentInstance,ImplementationFieldDescription
import os
from django.http.response import HttpResponse
from itertools import groupby
from operator import itemgetter
import subprocess
import io
import zipfile

from django.shortcuts import render, redirect,render_to_response

from scm.models import Play,Task,Attribute
from django.forms import ModelForm
from django.db.models  import fields
from django.forms import *
from django import  forms
from django.shortcuts import  get_object_or_404


#the host list generator 
def host_target_tuple_generator():
    #cette block va generer une liste de tuple  qui contient [(DEV1_jbossas,id_type),(DEV2_jboss,id_type).....]  
    listt=[]
    
    listt.append((None, '----------'))
     
    projects = Project.objects.\
                    prefetch_related('environment_set__component_instances__description','applications__logicalcomponent_set__implemented_by__instances','applications__logicalcomponent_set__implemented_by__technical_description').all() 
    
    for p in projects:                
      for apps in p.applications.all():
             for logical_coms in apps.logicalcomponent_set.all():
             
                  
                  listt.append((str([9500,apps.name+'_'+logical_coms.name.replace(" ","-")]),apps.name+'_'+logical_coms.name.replace(" ","-")))
                  
                  for component_implementationclass in logical_coms.implemented_by.all():
                       
                       listt.append((str([component_implementationclass.technical_description.name,component_implementationclass.name]).replace(" ","-"),component_implementationclass.name.replace(" ","-")))
               
                 
      
        
            #definition des environnemtns             
               
      for envt in p.environment_set.all():
          
           comps_instances=envt.component_instances.prefetch_related('instanciates').filter(deleted=False)
           rows = groupby(comps_instances, itemgetter('description'))
           
           groups = []
           uniquekeys = []
           
           for k, g in rows:
            groups.append(list(g))      
            uniquekeys.append(k)
           
                
           for x,y in zip(groups,uniquekeys):
               listt.append((str([y.name,envt.name+'_'+y.name]).replace(" ","-"),envt.name+'_'+y.name.replace(" ","-")))
                 
           
 
    # partie des composant mutuelles                
          
    comps_instances=ComponentInstance.objects.prefetch_related('environments','description').filter(deleted=False,environments__isnull=True)
    rows = groupby(comps_instances, itemgetter('description'))
    groups = []
    uniquekeys = []
    for k, g in rows:
      groups.append(list(g))      # Store group iterator as a list
      uniquekeys.append(k)
          
    for z in uniquekeys:
        
        listt.append((str([z.name,z.name]).replace(" ","-"),z.name.replace(" ","-")))
                
            
    print ('la liste :')
    #print (listt)  
   
    #print(listt,sep="\n")  
    for x in range(len(listt)):
     print listt[x]
    #return response         
    
    
    return listt




def zip_dir(directory, zipname):
    """
    Compress a directory (ZIP file).
    """
    if os.path.exists(directory):
        outZipFile = zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED)

        # The root directory within the ZIP file.
        rootdir = os.path.basename(directory)

        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:

                # Write the file named filename to the archive,
                # giving it the archive name 'arcname'.
                filepath   = os.path.join(dirpath, filename)
                parentpath = os.path.relpath(filepath, directory)
                arcname    = os.path.join(rootdir, parentpath)

                outZipFile.write(filepath, arcname)
                

    outZipFile.close()

from shutil import make_archive
from django.core.servers.basehttp import FileWrapper
def download(request,file_name="ansible_script"):
    """
    A django view to zip files in directory and send it as downloadable response to the browser.
    Args:
      @request: Django request object
      @file_name: Name of the directory to be zipped
    Returns:
      A downloadable Http response
    """
    #file_path = "/tmp/albums/"+file_name
    file_path=os.getcwd()+"/"+file_name
    # avec zip le nom des fichier qui contient é ne sont pas afficher
    path_to_zip = make_archive(file_path,"tar",file_path)
    response = HttpResponse(FileWrapper(file(path_to_zip,'rb')), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename='+file_name.replace(" ","_")+'.zip'
    return response




def zipdir(path, zipfile):
    # ziph is zipfile handle
    
    
    #rootdir = os.path.basename('ansible_script')
    for root, dirs, files in os.walk(path):
        
          
         
         
        for file in files:
            
            zipfile.write(os.path.join(root, file))

def zipping_ansible_dir_exported(path):
     zipf = zipfile.ZipFile('ansible.zip', 'w', zipfile.ZIP_DEFLATED)
     zipdir(path, zipf)
     zipf.close()




def generate_component_instances_mutual():
           mutual=''
                    
           mutual+='\n' 
            
           mutual+='[mutual:children]'
           mutual+='\n'
           comps_instances=ComponentInstance.objects.prefetch_related('environments','description').filter(deleted=False,environments__isnull=True)
           rows = groupby(comps_instances, itemgetter('description'))
           groups = []
           uniquekeys = []
           #data = sorted(data, key=keyfunc)
           for k, g in rows:
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
          
           for z in uniquekeys:
                mutual+=str(z.name)+'\n'
                
           for x,y in zip(groups,uniquekeys):
               mutual+='\n'
               mutual+='['+str(y.name)+']\n'
               for z in list(x): 
                   mutual+=z.name+'\n'                 
           
           #f = open("ansible_script/inventory/MAGE_inventory", "a")
           f = io.open("ansible_script/inventory/MAGE_inventory", 'a', encoding='utf8')
           
           print mutual
           f.write(mutual)
           f.close() 
           
           


def generate_component_instances_vars():
    
    component_instances = ComponentInstance.objects.\
                    prefetch_related('relationships__field_set','field_set__field','configurations','rel_target_set__field__link_type','rel_target_set__source','description__computed_field_set').all()
    
    
    
    
    
    print "beginning"                
    for component in   component_instances:
        g = io.open("ansible_script/inventory/host_vars/"+component.name, 'w', encoding='utf8')
        #g = open("ansible_script/inventory/host_vars/"+component.name, "w")
        componenet_var="---\n"
        #componenet_var+='#simple component fields\n'
        for simple in  component.field_set.all():
            componenet_var+=simple.field.name+':"'+simple.value+'"\n'
            
        """for e in component.relationships.all():
            componenet_var+=e.name+'\n'
        for e in component.rel_target_set.all():
               componenet_var+=str(e.field.target.name)+'\n'"""
        #implelemetationfields=ImplementationFieldDescription.objects.\
                    #prefetch_related('componentInstancefield_set__instance').filter(componentinstancefield__instance=component)
        
        #componenet_var+='#relational fields\n\n'
        for x,y in zip(component.rel_target_set.all(),component.relationships.all()):
            componenet_var+=x.field.target.name+':"'+y.name+'"\n'
        

        #componenet_var+='#calculated  fields\n\n'
        for des in component.description.computed_field_set.all() :
            componenet_var+=des.name+':"'+str(des.resolve(component))+'"\n'
        #for imp in implelemetationfields.ComponentInstancefield_set.all():
            #componenet_var+=imp.name+'\n' 
         
        
        
        
        """for ex in component.parameter_set.all():
            componenet_var+=ex.key+ex.value+'\n'
            print 'ddd'+ex.key+ex.value+'\n'"""
        
        
        
        #def resolve(self, instance):
        #return computed_field.resolve(component_instance)
        
        
        g.write(componenet_var)
        g.close()              

def ansible_inventory_export(request):
     
     current_directory = os.getcwd()
     final_directory = os.path.join(current_directory, r'ansible_script')
     inventory_path=os.path.join(final_directory, r'inventory')
     playbook_path=os.path.join(final_directory, r'playbooks')
     group_vars_path=os.path.join(inventory_path, r'group_vars')
     host_vars_path=os.path.join(inventory_path, r'host_vars')
     print final_directory
     if not os.path.exists(final_directory):
        os.makedirs(final_directory)
        os.makedirs(inventory_path)
        os.makedirs(playbook_path)
        os.makedirs(group_vars_path)
        os.makedirs(host_vars_path)
         
     
     """file_path = "/my/directory"
     directory = os.path.dirname(file_path)
     

     try:
        os.stat(directory)
     except:
         os.mkdir(ansible) """      

       
     inventory=''
     #f = open("ansible.txt", "w")
    
     
     print os.getcwd()
    
     #lister  tous nos  Projets (on a une seule projet pour la premiere version )
     projects = Project.objects.\
                    prefetch_related('environment_set__component_instances__description','applications__logicalcomponent_set__implemented_by__instances').all()
     
     
     
     inventory+='[Projects:children]\n'               
     for p in projects:
      inventory+=p.name+'\n'
     
     inventory+='\n'
     for p in projects:
        inventory+='['+p.name+':children]\n'
       
        for envt in p.environment_set.all():
           inventory+=envt.name+'\n'
          
       
        for apps in p.applications.all():
           inventory+=apps.name+'\n'
        
        
                
        for apps in p.applications.all():
            
           #comp=LogicalComponent.objects.filter(application=apps)
           inventory+='\n'
           inventory+='['+apps.name+':children]\n'
           for logical_coms in apps.logicalcomponent_set.all():
               inventory+=apps.name+'_'+logical_coms.name+'\n'
               
        
        
        for apps in p.applications.all():
            
           
           inventory+='\n'
           for logical_coms in apps.logicalcomponent_set.all():
              inventory+='\n'
              
              inventory+='['+apps.name+'_'+logical_coms.name+':children]\n'
              for component_implementationclass in logical_coms.implemented_by.all():
                 inventory+=component_implementationclass.name+'\n'
               
               
        
        for apps in p.applications.all():
            
           
           inventory+='\n'
           for logical_coms in apps.logicalcomponent_set.all():
              inventory+='\n'
              
              
              for component_implementationclass in logical_coms.implemented_by.all():
                 inventory+='\n'
                 
                 inventory+='['+component_implementationclass.name+']\n'
                 for instance in component_implementationclass.instances.filter(deleted=False):
                     inventory+=instance.name+'\n'
                     
        
        
        #definition des environnemtns             
        inventory+='\n'             
        for envt in p.environment_set.all():
           inventory+='\n' 
            
           inventory+='['+envt.name+':children]'
           inventory+='\n'
           comps_instances=envt.component_instances.prefetch_related('instanciates').filter(deleted=False)
           rows = groupby(comps_instances, itemgetter('description'))
           groups = []
           uniquekeys = []
           #data = sorted(data, key=keyfunc)
           for k, g in rows:
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
           #print (groups)
           #print '######'
           #print (uniquekeys) 
           
           for z in uniquekeys:
                inventory+=envt.name+'_'+z.name+'\n'
                
           for x,y in zip(groups,uniquekeys):
               inventory+='\n'
               inventory+='['+envt.name+'_'+y.name+']\n'
               for z in list(x): 
                   inventory+=z.name+'\n'  
           
           inventory+='\n'
           
          
                 
         
     #f = open("ansible_script/inventory/MAGE_inventory", "w")
     f = io.open("ansible_script/inventory/MAGE_inventory", 'w', encoding='utf8')
     f.write(inventory)
     f.close()    
         
     generate_component_instances_vars()
     generate_component_instances_mutual()
     
     #zipping_ansible_dir_exported(final_directory)
     #zip_dir(final_directory, 'ansible.zip')
     
     
     #makking the zip file downloadable for response 
     response=download(request,"ansible_script")
     
     
     #zipping 

     #cmd = subprocess.Popen('cmd.exe /K cd /')    
     
     return response
     #return redirect('welcome')
     
"""  ##################################################  inventory generator final solution   ##############################     """      
"""this is the seconde approche for generating the inventory because it appears that we should 
replace the white spaces in the hosts names with a caracter and  fixing the parser problem  for ansible inventory """ 

def generate_component_instances_mutual2():
           mutual=''
                    
           mutual+='\n' 
            
           
           comps_instances=ComponentInstance.objects.prefetch_related('environments','description').filter(deleted=False,environments__isnull=True)
           rows = groupby(comps_instances, itemgetter('description'))
           
           groups = []
           uniquekeys = []
           
           

           #data = sorted(data, key=keyfunc)
           for k, g in rows:
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
          
           for x,y in zip(groups,uniquekeys):
               mutual+='\n'
               mutual+='['+str(y.name)+']\n'
               for z in list(x): 
                   mutual+=z.name.replace(" ", "-")+'\n'  
           mutual+='\n' 
           mutual+='[mutual:children]'
           mutual+='\n'                            
          
           for z in uniquekeys:
                mutual+=str(z.name).replace(" ", "-")+'\n'
                
               
           
           #f = open("ansible_script/inventory/MAGE_inventory", "a")
           f = io.open("ansible_script/inventory/MAGE_inventory", 'a', encoding='utf8')
           
           print mutual
           f.write(mutual)
           f.close() 


def generate_component_instances_vars2():
    
    component_instances = ComponentInstance.objects.\
                    prefetch_related('relationships__field_set','field_set__field','configurations','rel_target_set__field__link_type','rel_target_set__source','description__computed_field_set').all()
    
    
    print "beginning"                
    for component in   component_instances:
        g = io.open("ansible_script/inventory/host_vars/"+component.name.replace(" ", "-"), 'w', encoding='utf8')
        #g = open("ansible_script/inventory/host_vars/"+component.name, "w")
        componenet_var="---\n"
        #componenet_var+='#simple component fields\n'
        for simple in  component.field_set.all():
            componenet_var+=simple.field.name+': "'+simple.value.replace(" ", "-")+'"\n'
            
        """for e in component.relationships.all():
            componenet_var+=e.name+'\n'
        for e in component.rel_target_set.all():
               componenet_var+=str(e.field.target.name)+'\n'"""
        #implelemetationfields=ImplementationFieldDescription.objects.\
                    #prefetch_related('componentInstancefield_set__instance').filter(componentinstancefield__instance=component)
        
        #componenet_var+='#relational fields\n\n'
        for x,y in zip(component.rel_target_set.all(),component.relationships.all()):
            componenet_var+=x.field.target.name+': "'+y.name.replace(" ", "-")+'"\n'
        

        #componenet_var+='#calculated  fields\n\n'
        for des in component.description.computed_field_set.all() :
            avant=des.name+': "'+str(des.resolve(component)).replace(" ", "-")
            componenet_var+=avant+'"\n'
            #componenet_var+=des.name+':"'+str(des.resolve(component))+'"\n'
        #for imp in implelemetationfields.ComponentInstancefield_set.all():
            #componenet_var+=imp.name+'\n' 
         
        
        
        
        """for ex in component.parameter_set.all():
            componenet_var+=ex.key+ex.value+'\n'
            print 'ddd'+ex.key+ex.value+'\n'"""
        
        
        
        #def resolve(self, instance):
        #return computed_field.resolve(component_instance)
        
        
        g.write(componenet_var)
        g.close()              



def ansible_inventory_export2(request):
     
     current_directory = os.getcwd()
     final_directory = os.path.join(current_directory, r'ansible_script')
     inventory_path=os.path.join(final_directory, r'inventory')
     playbook_path=os.path.join(final_directory, r'playbooks')
     group_vars_path=os.path.join(inventory_path, r'group_vars')
     host_vars_path=os.path.join(inventory_path, r'host_vars')
     print final_directory
     if not os.path.exists(final_directory):
        os.makedirs(final_directory)
        os.makedirs(inventory_path)
        os.makedirs(playbook_path)
        os.makedirs(group_vars_path)
        os.makedirs(host_vars_path)
         
         
     inventory=''  
     print os.getcwd()
     projects = Project.objects.\
                    prefetch_related('environment_set__component_instances__description','applications__logicalcomponent_set__implemented_by__instances').all()

                 
     
     inventory+='\n'
     for p in projects:
        
        #generation de la componenet implementation class 
        for apps in p.applications.all():
            
           
           inventory+='\n'
           for logical_coms in apps.logicalcomponent_set.all():
              inventory+='\n'
              
              
              for component_implementationclass in logical_coms.implemented_by.all():
                 inventory+='\n'
                 
                 inventory+='['+component_implementationclass.name+']\n'
                 for instance in component_implementationclass.instances.filter(deleted=False):
                     
                     inventory+=(instance.name).replace(" ", "-")+'\n'
        
        
        #generation of the logical component class 
        for apps in p.applications.all():
            
           
           inventory+='\n'
           for logical_coms in apps.logicalcomponent_set.all():
              inventory+='\n'
              
              inventory+='['+(apps.name+'_'+logical_coms.name).replace(" ", "-")+':children]\n'
              for component_implementationclass in logical_coms.implemented_by.all():
                 inventory+=component_implementationclass.name+'\n'
        
        
        #generation of the applications
        for apps in p.applications.all():
            
           #comp=LogicalComponent.objects.filter(application=apps)
           inventory+='\n'
           inventory+='['+apps.name+':children]\n'
           
           for logical_coms in apps.logicalcomponent_set.all():
               inventory+=(apps.name+'_'+logical_coms.name).replace(" ", "-")+'\n'
               
               
               
                        
        #definition des environnemtns             
        inventory+='\n'             
        for envt in p.environment_set.all():
           inventory+='\n' 
           
           
           
           
           comps_instances=envt.component_instances.prefetch_related('instanciates').filter(deleted=False)
           rows = groupby(comps_instances, itemgetter('description'))
           groups = []
           uniquekeys = []
           for k, g in rows:
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
            
           #generation des groupes des environnements grouppers
           for x,y in zip(groups,uniquekeys):
               inventory+='\n'
               inventory+='['+envt.name+'_'+y.name+']\n'
               for z in list(x): 
                   inventory+=z.name.replace(" ", "-")+'\n'  
           
           inventory+='\n'
           
           
           
           #generation de la super groupe d'environnements 
           inventory+='['+envt.name+':children]'
           inventory+='\n'
           
           #data = sorted(data, key=keyfunc)
           
         
           for z in uniquekeys:
                inventory+=envt.name+'_'+z.name+'\n'
                
        inventory+='\n'      
        #generation of the main project group
        inventory+='['+p.name+':children]\n'
        for envt in p.environment_set.all():
           inventory+=envt.name+'\n'  
        for apps in p.applications.all():
           inventory+=apps.name+'\n' 
         
         
         
     inventory+='\n'    
     inventory+='[Projects:children]\n'               
     for p in projects:
      inventory+=p.name+'\n'         
     #f = open("ansible_script/inventory/MAGE_inventory", "w")
     f = io.open("ansible_script/inventory/MAGE_inventory", 'w', encoding='utf8')
     f.write(inventory)
     f.close()    
         
     generate_component_instances_vars2()
     generate_component_instances_mutual2()
     
     
   
     response=download(request,"ansible_script")
     
     
      
     
     return response
       
  
LISS =((None, '----------'),
                        ('test', '1111'),
                        ('test', '2'),
                        ('test1', '45')) 
STRATEGY=((None, '----------'),
                        ('linear', 'linear'),
                        ('free ', 'free '),
                        ) 
LISS2=host_target_tuple_generator()

LISS =tuple(LISS2) 
   
     
class PlayForm(ModelForm):
      class Meta:
         model = Play
         fields = ['name', 'hosts', 'strategy']
         widgets={
     
               'hosts': Select(attrs={'cols': 5, 'rows': 1,'required': False},choices=LISS ),
               'strategy': Select(attrs={'cols': 5, 'rows': 1,'required': False},choices=STRATEGY ),
             }
 
      

#we install the first  play in the database and continue to the part1
def ansible_part0(request):
    
       
       
    
    if request.method == 'POST':
        play =Play.objects.create()
        form = PlayForm(request.POST, instance=play)
        if form.is_valid():
            form.save()
            
            return redirect('scm:manage_task', play_id=play.id)
            
            
    else:
        #the empty form
        
        """SAMPLE_CHOICES_LIST =((None, '----------'),
                        ('test', '1111'),
                        ('test', '2'),
                        ('test1', '45'))
        form = PlayForm(fields=('name', 'hosts', 'strategy',),widgets={
     
               'hosts': Select(attrs={'cols': 5, 'rows': 1,'required': False},choices=SAMPLE_CHOICES_LIST ),
             })"""
        form = PlayForm()
        return render_to_response("scm/ansible_part0.html", {'form': form})
    
    return response




   
     
     
   #generation de la liste de target
def ansible_part1(request):
    #cette block va generer une liste de tuple  qui contient [(DEV1_jbossas,id_type),(DEV2_jboss,id_type).....]  
    listt=[]
    tuple=()
    inventory=''
     
    projects = Project.objects.\
                    prefetch_related('environment_set__component_instances__description','applications__logicalcomponent_set__implemented_by__instances','applications__logicalcomponent_set__implemented_by__technical_description').all() 
    
    for p in projects:                
      for apps in p.applications.all():
             for logical_coms in apps.logicalcomponent_set.all():
             
                  
                  listt.append((apps.name+'_'+logical_coms.name,[9500,apps.name+'_'+logical_coms.name]))
                  
                  for component_implementationclass in logical_coms.implemented_by.all():
                       
                       listt.append((component_implementationclass.name,[component_implementationclass.technical_description.pk,component_implementationclass.name]))
               
                 
      
        
            #definition des environnemtns             
               
      for envt in p.environment_set.all():
          
           comps_instances=envt.component_instances.prefetch_related('instanciates').filter(deleted=False)
           rows = groupby(comps_instances, itemgetter('description'))
           
           groups = []
           uniquekeys = []
           
           for k, g in rows:
            groups.append(list(g))      
            uniquekeys.append(k)
           
                
           for x,y in zip(groups,uniquekeys):
               listt.append((envt.name+'_'+y.name,[9600,y.name]))
                 
           
 
    # partie des composant mutuelles                
          
    comps_instances=ComponentInstance.objects.prefetch_related('environments','description').filter(deleted=False,environments__isnull=True)
    rows = groupby(comps_instances, itemgetter('description'))
    groups = []
    uniquekeys = []
    for k, g in rows:
      groups.append(list(g))      # Store group iterator as a list
      uniquekeys.append(k)
          
    for z in uniquekeys:
        
        listt.append((z.name,[9500,z.name]))
                
            
    print ('la liste :')
    #print (listt)  
   
    #print(listt,sep="\n")  
    for x in range(len(listt)):
     print listt[x]
    #return response         
    
    
    return redirect('welcome') 
     
     

     
def ansible_testing(request):
    attribute1=Attribute.objects.create(name="url",mannuel_value="htttps:url1")
    attribute2=Attribute.objects.create(name="url2",automatique_value="htttps:url2")
    task1=Task.objects.create(name="deployer ue script ",module_name="unzip module",delegate_to="os server1")

    task1.attributes.add(attribute1,attribute2)
    play1=Play.objects.create(name="play1",hosts="DEV1_jqm",strategy="linear")
    play1.tasks.add(task1)
    plays=Play.objects.all()
    print plays
    
    
    return redirect('welcome')     
     
def ansible_testing2(request):
    plays=Play.objects.all()
    play.delete()
    print ('deleted succefully')
    #for p in plays :
    # print p.name
      
    return redirect('welcome')      



#the function that read from the play instance and generate the playbook
def generate_the_playbook(play_id):
     
     play = get_object_or_404(Play, id=play_id)
     #extraction of the taget name 
     hosts=play.hosts
     description_list=hosts.split(',')
     
     target_ugly=description_list[1]
     target=target_ugly[:(len(target_ugly)-1)]
     target_name=str(target)
     target_name=target_name[3:(len(target_name)-1)]
     print 'the target name is '+ target_name
     
     playbook='---'
     playbook+='\n\n'
     playbook+='- name: '+'"'+play.name+'"'+'\n'
     playbook+='  hosts: '+target_name+'\n'
     playbook+='  strategy: '+play.strategy+'\n'
     playbook+='  tasks:'+'\n'
     for task in play.tasks.all():
         playbook+='\n'
         playbook+='  - name:'+task.name+'\n'
         playbook+='    '+task.module_name+':\n'
         for attribute in task.attributes.all():
             playbook+='      '+attribute.name+': '
             manuel_value=attribute.mannuel_value
             automatique_value=attribute.automatique_value
             if manuel_value !="" :
                  playbook+='"'+manuel_value+'"\n'
             else:
                 playbook+='"{{'+automatique_value+'}}"\n'
         if task.delegate_to !="" :
           playbook+='    '+'delegate_to: '+'"{{'+task.delegate_to+'}}"\n'
             
     
     #preparation de la fichier du playbook
     current_directory = os.getcwd()
     final_directory = os.path.join(current_directory, r'ansible_script')
     playbook_path=os.path.join(final_directory, r'playbooks')
     if not os.path.exists(final_directory):
        os.makedirs(final_directory)
        os.makedirs(playbook_path)
       
         
     
     f = io.open("ansible_script/playbooks/mage_playbook.yml", 'w', encoding='utf8')
           
     print playbook
     f.write(playbook)
     f.close() 
    
     return 
 
 
 
 
 
 
 