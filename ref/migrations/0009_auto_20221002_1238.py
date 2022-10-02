# Generated by Django 3.2.15 on 2022-10-02 10:38

from django.db import migrations


def forward(apps, schema_editor):
    Project = apps.get_model('ref', 'Project')
    default_project = Project.objects.first() or Project.objects.get_or_create(name='NEW_PROJECT', defaults={'description': "Created by database upgrade. Rename it as you wish"})[0]
    default_project.save()

    ComponentInstance = apps.get_model('ref', 'ComponentInstance')
    for ci in ComponentInstance.objects.all():
        if not ci.project:
            if ci.environments.exists():
                ci.project = ci.environments.first().project
            else:
                ci.project = default_project

            ci.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ref', '0008_componentinstance_project'),
    ]

    operations = [
        migrations.RunPython(forward),
    ]