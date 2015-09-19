# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ref', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdministrationUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('alternate_name_1', models.CharField(max_length=100, null=True, blank=True)),
                ('alternate_name_2', models.CharField(max_length=100, null=True, blank=True)),
                ('alternate_name_3', models.CharField(max_length=100, null=True, blank=True)),
                ('description', models.CharField(max_length=500)),
                ('parent', models.ForeignKey(blank=True, to='ref.AdministrationUnit', null=True)),
            ],
            options={
                'verbose_name': 'projet',
                'verbose_name_plural': 'projets',
            },
        ),
        migrations.AlterField(
            model_name='application',
            name='project',
            field=models.ForeignKey(related_name='applications', to='ref.AdministrationUnit'),
        ),
        migrations.AlterField(
            model_name='componentinstance',
            name='environments',
            field=models.ManyToManyField(related_name='component_instances', verbose_name=b'environnements ', to='ref.Environment', blank=True),
        ),
        migrations.AlterField(
            model_name='conventioncounter',
            name='scope_project',
            field=models.ForeignKey(default=None, blank=True, to='ref.AdministrationUnit', null=True),
        ),
        migrations.AlterField(
            model_name='environment',
            name='project',
            field=models.ForeignKey(to='ref.AdministrationUnit'),
        ),
        migrations.AlterField(
            model_name='environment',
            name='show_sensitive_data',
            field=models.NullBooleanField(verbose_name=b'afficher les informations sensibles', choices=[(None, 'd\xe9fini par la typologie'), (False, b'cacher'), (True, b'montrer')]),
        ),
        migrations.AlterField(
            model_name='environment',
            name='typology',
            field=models.ForeignKey(verbose_name='typologie', to='ref.EnvironmentType'),
        ),
        migrations.AlterField(
            model_name='implementationfielddescription',
            name='datatype',
            field=models.CharField(default=b'str', max_length=20, verbose_name='type', choices=[(b'str', b'cha\xc3\xaene de caract\xc3\xa8res'), (b'int', b'entier'), (b'bool', b'bool\xc3\xa9en')]),
        ),
        migrations.AlterField(
            model_name='mageparam',
            name='app',
            field=models.CharField(max_length=5, verbose_name='application', choices=[(b'ref', b'ref'), (b'scm', b'scm')]),
        ),
        migrations.DeleteModel(
            name='Project',
        ),
        migrations.AddField(
            model_name='implementationdescription',
            name='project',
            field=models.ForeignKey(related_name='descriptions', default=0, verbose_name=b'projet', to='ref.AdministrationUnit'),
            preserve_default=False,
        ),
    ]
