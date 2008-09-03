from MAGE.ref.models import Composant


## Global compat test
def arePrerequisitesVerified(envt_name, is_tocheck):
    areVerified = True
    for prereq in is_tocheck.requirements.all():
        rs = Composant.objects.filter(environments__name=envt_name, name=prereq.component_name, type=prereq.component_type)
        if rs.count() == 0:
            print u"L'IS %s a besoin d'au moins un composant de type %s en version %s, mais ce type de composant \
                n'existe pas dans l'environnement %s" %(prereq.component_type, prereq.version, envt_name) 
            areVerified = False
        for compo in rs.all():
            if compo.version != prereq.version:
                print u"Le composant %s est en version %s, alors que l'installation requiert la version %s" \
                    %(compo, compo.version, prereq.version)
                areVerified = False
    return areVerified

