# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('ref', '0002_auto_20150919_1221'),
    ]

    operations = [
        migrations.CreateModel(
            name='AclAuthorization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grant', models.IntegerField(default=0, choices=[(0, b'Allow'), (1, b'Forbid')])),
                ('codename', models.CharField(db_index=True, max_length=20, choices=[(b'read_folder', b'Afficher les caract\xc3\xa9ristiques du dossier'), (b'modify_folder', b'Modifier les caract\xc3\xa9ristiques du dossier'), (b'list_envt', b'Afficher la liste des environnements contenus'), (b'list_folders', b'Afficher la liste des sous dossiers contenus'), (b'add_envt', b'Cr\xc3\xa9er un environnement'), (b'delete_envt', b'Supprimer un environnement'), (b'add_folder', b'Ajouter un sous dossier'), (b'delete_folder', b'Supprimer un sous-dossier vide'), (b'read_envt', b'Afficher le d\xc3\xa9tail des environnements (sauf informations sensibles)'), (b'read_envt_sensible', b'Afficher les information sensibles des environnements'), (b'change_envt', b'Modifier un environnement (sauf informations sensibles)'), (b'change_envt_sensible', b"Modifier les informations sensibles d'un environnement")])),
                ('group', models.ForeignKey(to='auth.Group')),
            ],
        ),
        migrations.AddField(
            model_name='administrationunit',
            name='block_inheritance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='project',
            field=models.ForeignKey(verbose_name=b'si hors environnement classer dans', blank=True, to='ref.AdministrationUnit', null=True),
        ),
        migrations.AlterField(
            model_name='administrationunit',
            name='parent',
            field=models.ForeignKey(related_name='subfolders', blank=True, to='ref.AdministrationUnit', null=True),
        ),
        migrations.AddField(
            model_name='aclauthorization',
            name='target',
            field=models.ForeignKey(verbose_name=b'cible', to='ref.AdministrationUnit'),
        ),
    ]
