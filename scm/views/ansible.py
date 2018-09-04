# coding: utf-8
from ref.models import Environment,Project,LogicalComponent,ComponentInstance,ImplementationFieldDescription
import os
from django.http.response import HttpResponse
from itertools import groupby
from operator import itemgetter
import subprocess
import io
import zipfile

from django.shortcuts import render, redirect


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
     """with open('ansible.txt', 'r') as fh:
            #response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response = HttpResponse(fh.read(),content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'inline; filename="ansible.txt"'
            #response['Content-Disposition'] = 'inline; filename=' + os.path.basename('ansible.txt')
  """          
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
           
           """
           for x,y in zip(groups,uniquekeys):
               
               for z in list(x): 
                 print z.name
                 if z.instanciates is not None:
                      
                    print 'this is instanciates'
                 else :
                      print 'not instanciates'   
               print 'la description qui vient avec ces component instance  '
               print y.description
               """
      
           """inventory+=str(p.id)+'_'+envt.name+':children]'
           for x,y in zip(groups,uniquekeys):
               print x 
               
               print y.description
           
           print '##########################################################'"""
                 
         
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