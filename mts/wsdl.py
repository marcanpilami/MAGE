from SOAPpy import WSDL

wsdlFile = 'http://192.168.127.22/mantis/mc/mantisconnect.php?wsdl'
server = WSDL.Proxy(wsdlFile)
print server.methods.keys()

callInfo = server.methods['mc_version']
print callInfo.inparams


## Try it
server.soapproxy.config.dumpSOAPOut = 1
server.soapproxy.config.dumpSOAPIn = 1
server.soapproxy.namespaceStyle = 2001
server.mc_version()