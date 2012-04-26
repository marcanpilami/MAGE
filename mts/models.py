# encoding: UTF-8

#from django.db import models

from MAGE.mkl.models import Ticket

from SOAPpy import SOAPProxy

class SoapToolbox:
    def __init__(self, debug = False):
        # TODO : look for parameters, not hard coded values. Debug should be one too.
        self.url = 'http://192.168.116.128/mantis/mc/mantisconnect.php'
        self.namespace = 'http://futureware.biz/mantisconnect'
        self.login = 'administrator'
        self.password = "root"
        self.server = SOAPProxy(self.url, self.namespace)
        
        if debug:
            self.server.config.dumpSOAPOut = 1
            self.server.config.dumpSOAPIn = 1
        
        #print self.server.mc_enum_priorities(self.login, self.password)

## The one and only toolbox
#toolbox = SoapToolbox(True)
toolbox = SoapToolbox()


def getTicket(id):
    res = toolbox.server.mc_issue_get(toolbox.login, toolbox.password, id)
    print res
    tk = Ticket(id, res['summary'], res['description'], res['reporter'], res['reporter'])
    return tk

def updateTicket(id, field_name, new_value):
    print "Mise à jour du ticket %s : champ %s prend la valeur %s" %(id, field_name, new_value)





def create_issue():
    id = {'id'              : 2,
          'view_state'      : 0,
          'last_updatde'    : None,
          'project'         : None,             # tns:ObjectRef
          'category'        : 'A',              # xsd:string
          'priority'        : None,             # tns:ObjectRef
          'severity'        : None,             # "
          'status'          : 1,
          'reporter'        : 'administrator',  # tns:AccountData
          'summary'         : 'essai 1',        # xsd:string
          'version'         : '__NO_ENV__',     # xsd;string
          'build'           : '1',
          'platform'        : None,
          'os'              : None,
          'os_build'        : None,
          'reproductibility': None,             # tns:ObjectRef
          'date_submitted'  : None,
          'sponsorship_total':0,
          'handler'         : 'administrator',  # tns:accountData
          'projection'      : None          ,   # tns:ObjectRef
          'eta'             : None,             # tns:ObjectRef
          'resolution'      : None,             # "
          'fixed_in_version': None,             # xsd:string
          'description'     : "pouet",          # xsd:string
          'steps_to_reproduce': None,           # xsd:string
          'additional_information': None,       # xsd:string
          
          
          
          
          
          }
          
    toolbox.server.issue_add(toolbox.login, toolbox.password, id)

print getTicket(1)

#create_issue()