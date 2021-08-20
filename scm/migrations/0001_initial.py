# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import scm.models


class Migration(migrations.Migration):

    dependencies = [
        ('ref', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BackupItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BackupRestoreMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'm\xe9thode de restauration par d\xe9faut',
                'verbose_name_plural': 'm\xe9thodes de restauration par d\xe9faut',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComponentInstanceConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_on', models.DateTimeField()),
                ('install_failure', models.BooleanField(default=False)),
                ('component_instance', models.ForeignKey(related_name='configurations', to='ref.ComponentInstance', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstallableItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_full', models.BooleanField(default=False, verbose_name=u'installation de zéro')),
                ('data_loss', models.BooleanField(default=False, verbose_name=u'entraine des pertes de données')),
                ('datafile', models.FileField(upload_to=scm.models.__iidatafilename__, null=True, verbose_name='fichier', blank=True)),
            ],
            options={
                'permissions': (('download_ii', 'can download the installation file'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstallableSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=40, verbose_name='r\xe9f\xe9rence')),
                ('description', models.CharField(max_length=1000, null=True, verbose_name='r\xe9sum\xe9 du contenu', blank=True)),
                ('set_date', models.DateTimeField(auto_now_add=True, verbose_name='date de r\xe9ception')),
                ('ticket_list', models.CharField(max_length=100, null=True, verbose_name=u'ticket(s) lié(s) séparés par une virgule', blank=True)),
                ('status', models.IntegerField(default=3, choices=[(1, 'VALIDATED'), (2, 'TESTED'), (3, 'HANDEDOFF')])),
                ('location_data_1', models.CharField(max_length=100, null=True, blank=True)),
                ('location_data_2', models.CharField(max_length=100, null=True, blank=True)),
                ('location_data_3', models.CharField(max_length=100, null=True, blank=True)),
                ('location_data_4', models.CharField(max_length=100, null=True, blank=True)),
                ('datafile', models.FileField(upload_to=scm.models.__isetdatafilename__, null=True, verbose_name='fichier', blank=True)),
                ('removed', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'permissions': (('validate_installableset', 'can change the status of the set'), ('install_installableset', 'can reference an installation')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Delivery',
            fields=[
                ('installableset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scm.InstallableSet', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=('scm.installableset',),
        ),
        migrations.CreateModel(
            name='BackupSet',
            fields=[
                ('installableset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scm.InstallableSet', on_delete=models.CASCADE)),
                ('from_envt', models.ForeignKey(blank=True, to='ref.Environment', null=True, on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=('scm.installableset',),
        ),
        migrations.CreateModel(
            name='Installation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('asked_in_ticket', models.CharField(max_length=10, null=True, verbose_name=u'ticket lié ', blank=True)),
                ('install_date', models.DateTimeField(verbose_name='date d\\installation ')),
                ('installed_set', models.ForeignKey(verbose_name=u'livraison appliquée ', to='scm.InstallableSet', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstallationMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=254, verbose_name='nom')),
                ('halts_service', models.BooleanField(default=True, verbose_name='arr\xeat de service')),
                ('available', models.BooleanField(default=True, verbose_name='disponible')),
                ('restoration_only', models.BooleanField(default=False, verbose_name='op\xe9ration purement de restauration')),
            ],
            options={
                'verbose_name': "m\xe9thode d'installation",
                'verbose_name_plural': "m\xe9thodes d'installation",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemDependency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operator', models.CharField(default='==', max_length=2, choices=[('>=', '>='), ('<=', '<='), ('==', '==')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogicalComponentVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=50)),
                ('logical_component', models.ForeignKey(related_name='versions', to='ref.LogicalComponent', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PackageChecker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.CharField(max_length=200, verbose_name='Python module containing the checker class')),
                ('name', models.CharField(max_length=200, verbose_name='Python checker class name')),
                ('description', models.CharField(max_length=200, verbose_name='description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetDependency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operator', models.CharField(max_length=2, choices=[('>=', '>='), ('<=', '<='), ('==', '==')])),
                ('depends_on_version', models.ForeignKey(to='scm.LogicalComponentVersion', on_delete=models.CASCADE)),
                ('installable_set', models.ForeignKey(related_name='requirements', to='scm.InstallableSet', on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=40, verbose_name='r\xe9f\xe9rence')),
                ('snapshot_date', models.DateTimeField(auto_now_add=True, verbose_name='date de prise de la photo')),
                ('from_envt', models.ForeignKey(to='ref.Environment', on_delete=models.CASCADE)),
                ('versions', models.ManyToManyField(to='scm.LogicalComponentVersion', verbose_name='version des composants')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='itemdependency',
            name='depends_on_version',
            field=models.ForeignKey(to='scm.LogicalComponentVersion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='itemdependency',
            name='installable_item',
            field=models.ForeignKey(related_name='dependencies', to='scm.InstallableItem', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installationmethod',
            name='checkers',
            field=models.ManyToManyField(related_name='used_in', to='scm.PackageChecker', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installationmethod',
            name='method_compatible_with',
            field=models.ManyToManyField(related_name='installation_methods', verbose_name="permet d'installer", to='ref.ComponentImplementationClass'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installableitem',
            name='belongs_to_set',
            field=models.ForeignKey(related_name='set_content', to='scm.InstallableSet', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installableitem',
            name='how_to_install',
            field=models.ManyToManyField(to='scm.InstallationMethod', verbose_name="peut s'installer avec"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installableitem',
            name='what_is_installed',
            field=models.ForeignKey(related_name='installed_by', to='scm.LogicalComponentVersion', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstanceconfiguration',
            name='part_of_installation',
            field=models.ForeignKey(related_name='modified_components', to='scm.Installation', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstanceconfiguration',
            name='result_of',
            field=models.ForeignKey(to='scm.InstallableItem', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backuprestoremethod',
            name='method',
            field=models.ForeignKey(to='scm.InstallationMethod', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backuprestoremethod',
            name='target',
            field=models.ForeignKey(related_name='restore_methods', verbose_name='cible', to='ref.ComponentImplementationClass', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='backupset',
            field=models.ForeignKey(related_name='all_items', to='scm.BackupSet', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='instance',
            field=models.ForeignKey(to='ref.ComponentInstance', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='instance_configuration',
            field=models.ForeignKey(blank=True, to='scm.ComponentInstanceConfiguration', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='related_scm_install',
            field=models.ForeignKey(blank=True, to='scm.InstallableItem', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
