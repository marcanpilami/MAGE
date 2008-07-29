from MAGE.liv.models import *
from MAGE.ref.models import *
from MAGE.gcl.models import *
from MAGE.mqqm.models import *

e = Environment.objects.get(pk=1)
d = Delivery.objects.all()[0]
#d.installOn(e)
mq = QueueManager.objects.all()[0]
print mq
ver = getComponentVersion(mq)
print ver
Tag.snapshot('TAG1', 'ENVT1')