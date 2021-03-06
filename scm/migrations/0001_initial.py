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
                ('component_instance', models.ForeignKey(related_name='configurations', to='ref.ComponentInstance')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InstallableItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_full', models.BooleanField(default=False, verbose_name=b'installation de z\xc3\xa9ro')),
                ('data_loss', models.BooleanField(default=False, verbose_name='entraine des pertes de donn\xe9es')),
                ('datafile', models.FileField(upload_to=scm.models.__iidatafilename__, null=True, verbose_name=b'fichier', blank=True)),
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
                ('ticket_list', models.CharField(max_length=100, null=True, verbose_name=b'ticket(s) li\xc3\xa9(s) s\xc3\xa9par\xc3\xa9s par une virgule', blank=True)),
                ('status', models.IntegerField(default=3, choices=[(1, b'VALIDATED'), (2, b'TESTED'), (3, b'HANDEDOFF')])),
                ('location_data_1', models.CharField(max_length=100, null=True, blank=True)),
                ('location_data_2', models.CharField(max_length=100, null=True, blank=True)),
                ('location_data_3', models.CharField(max_length=100, null=True, blank=True)),
                ('location_data_4', models.CharField(max_length=100, null=True, blank=True)),
                ('datafile', models.FileField(upload_to=scm.models.__isetdatafilename__, null=True, verbose_name=b'fichier', blank=True)),
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
                ('installableset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scm.InstallableSet')),
            ],
            options={
            },
            bases=('scm.installableset',),
        ),
        migrations.CreateModel(
            name='BackupSet',
            fields=[
                ('installableset_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='scm.InstallableSet')),
                ('from_envt', models.ForeignKey(blank=True, to='ref.Environment', null=True)),
            ],
            options={
            },
            bases=('scm.installableset',),
        ),
        migrations.CreateModel(
            name='Installation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('asked_in_ticket', models.CharField(max_length=10, null=True, verbose_name=b'ticket li\xc3\xa9 ', blank=True)),
                ('install_date', models.DateTimeField(verbose_name=b'date d\\installation ')),
                ('installed_set', models.ForeignKey(verbose_name=b'livraison appliqu\xc3\xa9e ', to='scm.InstallableSet')),
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
                ('operator', models.CharField(default=b'==', max_length=2, choices=[(b'>=', b'>='), (b'<=', b'<='), (b'==', b'==')])),
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
                ('logical_component', models.ForeignKey(related_name='versions', to='ref.LogicalComponent')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PackageChecker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module', models.CharField(max_length=200, verbose_name=b'Python module containing the checker class')),
                ('name', models.CharField(max_length=200, verbose_name=b'Python checker class name')),
                ('description', models.CharField(max_length=200, verbose_name=b'description')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SetDependency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('operator', models.CharField(max_length=2, choices=[(b'>=', b'>='), (b'<=', b'<='), (b'==', b'==')])),
                ('depends_on_version', models.ForeignKey(to='scm.LogicalComponentVersion')),
                ('installable_set', models.ForeignKey(related_name='requirements', to='scm.InstallableSet')),
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
                ('from_envt', models.ForeignKey(to='ref.Environment')),
                ('versions', models.ManyToManyField(to='scm.LogicalComponentVersion', verbose_name='version des composants')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='itemdependency',
            name='depends_on_version',
            field=models.ForeignKey(to='scm.LogicalComponentVersion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='itemdependency',
            name='installable_item',
            field=models.ForeignKey(related_name='dependencies', to='scm.InstallableItem'),
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
            field=models.ForeignKey(related_name='set_content', to='scm.InstallableSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installableitem',
            name='how_to_install',
            field=models.ManyToManyField(to='scm.InstallationMethod', verbose_name=b"peut s'installer avec"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='installableitem',
            name='what_is_installed',
            field=models.ForeignKey(related_name='installed_by', to='scm.LogicalComponentVersion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstanceconfiguration',
            name='part_of_installation',
            field=models.ForeignKey(related_name='modified_components', to='scm.Installation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstanceconfiguration',
            name='result_of',
            field=models.ForeignKey(to='scm.InstallableItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backuprestoremethod',
            name='method',
            field=models.ForeignKey(to='scm.InstallationMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backuprestoremethod',
            name='target',
            field=models.ForeignKey(related_name='restore_methods', verbose_name=b'cible', to='ref.ComponentImplementationClass'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='backupset',
            field=models.ForeignKey(related_name='all_items', to='scm.BackupSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='instance',
            field=models.ForeignKey(to='ref.ComponentInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='instance_configuration',
            field=models.ForeignKey(blank=True, to='scm.ComponentInstanceConfiguration', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='backupitem',
            name='related_scm_install',
            field=models.ForeignKey(blank=True, to='scm.InstallableItem', null=True),
            preserve_default=True,
        ),
    ]
