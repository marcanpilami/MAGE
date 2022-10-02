if (! (Test-Path $PSScriptRoot/html ))
{
    mkdir $PSScriptRoot/html
}
& sphinx-build.exe -a -b html $PSScriptRoot $PSScriptRoot/html

# For updating the class diagrams with django_extensions enabled
# python .\manage.py graph_models --pydot -g -o ./doc/media/full.png scm ref
# python .\manage.py graph_models --pydot -g -o ./doc/media/scm.png --include-models InstallableSet,InstallableItem,LogicalComponentVersion,InstallationMethod,Installation,ComponentInstanceConfiguration,LogicalComponentVersion,Application,Project,ComponentInstance,Environment,LogicalComponent,ComponentImplementationClass scm ref