# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('alternate_name_1', models.CharField(max_length=100, null=True, blank=True)),
                ('alternate_name_2', models.CharField(max_length=100, null=True, blank=True)),
                ('alternate_name_3', models.CharField(max_length=100, null=True, blank=True)),
                ('description', models.CharField(max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComponentImplementationClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'code')),
                ('description', models.CharField(max_length=500)),
                ('ref1', models.CharField(max_length=20, null=True, verbose_name='ref\xe9rence 1', blank=True)),
                ('ref2', models.CharField(max_length=20, null=True, verbose_name='ref\xe9rence 2', blank=True)),
                ('ref3', models.CharField(max_length=20, null=True, verbose_name='ref\xe9rence 3', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='utilis\xe9')),
            ],
            options={
                'verbose_name': 'offre impl\xe9mentant un composant logique',
                'verbose_name_plural': 'offres impl\xe9mentant des composants logiques',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComponentInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('deleted', models.BooleanField(default=False)),
                ('include_in_envt_backup', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'instance de composant',
                'verbose_name_plural': 'instances de composant',
                'permissions': (('allfields_componentinstance', 'access all fields including restricted ones'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComponentInstanceField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.CharField(max_length=255, verbose_name=b'valeur', db_index=True)),
            ],
            options={
                'verbose_name': 'valeur de champ',
                'verbose_name_plural': 'valeurs des champs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComponentInstanceRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'valeur de relation',
                'verbose_name_plural': 'valeurs des relations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConventionCounter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scope_instance', models.IntegerField(default=None, null=True, blank=True)),
                ('val', models.IntegerField(default=0, verbose_name=b'valeur courante')),
                ('scope_application', models.ForeignKey(default=None, blank=True, to='ref.Application', null=True)),
            ],
            options={
                'verbose_name': 'Compteur convention nommage',
                'verbose_name_plural': 'Compteurs convention nommage',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name=b'Nom')),
                ('buildDate', models.DateField(auto_now_add=True, verbose_name='Date de cr\xe9ation')),
                ('destructionDate', models.DateField(null=True, verbose_name='Date de suppression pr\xe9vue', blank=True)),
                ('description', models.CharField(max_length=500)),
                ('manager', models.CharField(max_length=100, null=True, verbose_name=b'responsable', blank=True)),
                ('template_only', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True, verbose_name='utilis\xe9')),
                ('show_sensitive_data', models.NullBooleanField(verbose_name=b'afficher les informations sensibles')),
                ('managed', models.BooleanField(default=True, verbose_name='administr\xe9')),
            ],
            options={
                'verbose_name': 'environnement',
                'verbose_name_plural': 'environnements',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnvironmentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name=b'Nom')),
                ('description', models.CharField(max_length=500, verbose_name=b'description')),
                ('short_name', models.CharField(max_length=10, verbose_name=b'code', db_index=True)),
                ('chronological_order', models.IntegerField(default=1, verbose_name=b"ordre d'affichage")),
                ('default_show_sensitive_data', models.BooleanField(default=False, verbose_name=b'afficher les informations sensibles')),
                ('implementation_patterns', models.ManyToManyField(to='ref.ComponentImplementationClass', blank=True)),
            ],
            options={
                'verbose_name': 'classification des environnements',
                'verbose_name_plural': 'classifications des environnements',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedParameter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=50, verbose_name=b'clef')),
                ('value', models.CharField(max_length=100, verbose_name=b'valeur')),
                ('instance', models.ForeignKey(related_name='parameter_set', to='ref.ComponentInstance')),
            ],
            options={
                'verbose_name': 'param\xe8tre \xe9tendu',
                'verbose_name_plural': 'param\xe8tres \xe9tendus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImplementationComputedFieldDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'nom court du champ')),
                ('label', models.CharField(max_length=150, verbose_name=b'label')),
                ('label_short', models.CharField(help_text='si vide, label sera utilis\xe9', max_length=30, null=True, verbose_name=b'label court', blank=True)),
                ('help_text', models.CharField(max_length=254, null=True, verbose_name=b'aide descriptive du champ', blank=True)),
                ('sensitive', models.BooleanField(default=False, verbose_name=b'sensible')),
                ('pattern', models.CharField(max_length=500, verbose_name=b'cha\xc3\xaene de calcul')),
                ('widget_row', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'champ calcul\xe9',
                'verbose_name_plural': 'champs calcul\xe9s',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImplementationDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'nom', db_index=True)),
                ('description', models.CharField(max_length=500, verbose_name=b'description')),
                ('tag', models.CharField(db_index=True, max_length=100, null=True, verbose_name='cat\xe9gorie', blank=True)),
                ('include_in_default_envt_backup', models.BooleanField(default=False, verbose_name='inclure dans les backups par d\xe9faut')),
                ('self_description_pattern', models.CharField(help_text='sera utilis\xe9 pour toutes les descriptions par d\xe9faut des instances de composant. Utilise les m\xeame motifs (patterns) que les champs dynamiques.', max_length=500, verbose_name=b"motif d'auto description")),
            ],
            options={
                'verbose_name': 'description instance',
                'verbose_name_plural': 'descriptions instances',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImplementationFieldDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'nom court du champ')),
                ('label', models.CharField(max_length=150, verbose_name=b'label')),
                ('label_short', models.CharField(help_text='si vide, label sera utilis\xe9', max_length=30, null=True, verbose_name=b'label court', blank=True)),
                ('help_text', models.CharField(max_length=254, null=True, verbose_name=b'aide descriptive du champ', blank=True)),
                ('sensitive', models.BooleanField(default=False, verbose_name=b'sensible')),
                ('compulsory', models.BooleanField(default=True)),
                ('default', models.CharField(max_length=500, null=True, verbose_name=b'd\xc3\xa9faut', blank=True)),
                ('datatype', models.CharField(default=b'str', max_length=20, verbose_name='type', choices=[(b'str', b'cha\xc3\xaene de caract\xc3\xa8res'), (b'int', b'entier')])),
                ('widget_row', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('description', models.ForeignKey(related_name='field_set', verbose_name='impl\xe9mentation m\xe8re', to='ref.ImplementationDescription')),
            ],
            options={
                'verbose_name': 'champ simple',
                'verbose_name_plural': 'champs simples',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImplementationRelationDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'nom court du champ')),
                ('label', models.CharField(max_length=150, verbose_name=b'label')),
                ('label_short', models.CharField(help_text='si vide, label sera utilis\xe9', max_length=30, null=True, verbose_name=b'label court', blank=True)),
                ('help_text', models.CharField(max_length=254, null=True, verbose_name=b'aide descriptive du champ', blank=True)),
                ('sensitive', models.BooleanField(default=False, verbose_name=b'sensible')),
                ('min_cardinality', models.IntegerField(default=0)),
                ('max_cardinality', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'relation',
                'verbose_name_plural': 'relations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImplementationRelationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, verbose_name=b'type relation')),
                ('label', models.CharField(max_length=100, verbose_name=b'label')),
            ],
            options={
                'verbose_name': 'classification des relations',
                'verbose_name_plural': 'classifications des relations',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(verbose_name=b'URL cible')),
                ('legend', models.CharField(max_length=100, verbose_name=b'l\xc3\xa9gende du lien')),
                ('color', models.CharField(help_text=b'couleur au format #RRGGBB hexad\xc3\xa9cimal. Ex: #FF00CC', max_length=7, verbose_name=b'couleur')),
            ],
            options={
                'verbose_name': 'lien page accueil',
                'verbose_name_plural': 'liens page accueil',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LogicalComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=b'nom')),
                ('description', models.CharField(max_length=500)),
                ('scm_trackable', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True, verbose_name='utilis\xe9')),
                ('ref1', models.CharField(max_length=20, null=True, verbose_name='ref\xe9rence 1', blank=True)),
                ('ref2', models.CharField(max_length=20, null=True, verbose_name='ref\xe9rence 2', blank=True)),
                ('ref3', models.CharField(max_length=20, null=True, verbose_name='ref\xe9rence 3', blank=True)),
                ('application', models.ForeignKey(to='ref.Application')),
            ],
            options={
                'verbose_name': 'composant logique',
                'verbose_name_plural': 'composants logiques',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MageParam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=30, verbose_name='cl\xe9')),
                ('app', models.CharField(max_length=5, verbose_name='application', choices=[(b'crispy_forms', b'crispy_forms'), (b'ref', b'ref'), (b'scm', b'scm'), (b'debug_toolbar', b'debug_toolbar')])),
                ('value', models.CharField(max_length=100, verbose_name='valeur')),
                ('description', models.CharField(max_length=200, null=True, verbose_name='description', blank=True)),
                ('default_value', models.CharField(max_length=100, null=True, verbose_name='valeur par d\xe9faut', blank=True)),
                ('axis1', models.CharField(max_length=30, null=True, verbose_name='classification optionnelle', blank=True)),
                ('restricted', models.BooleanField(default=False)),
                ('model', models.ForeignKey(verbose_name='mod\xe8le concern\xe9', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ['app', 'key'],
                'verbose_name': 'param\xe8tre global',
                'verbose_name_plural': 'param\xe8tres globaux',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('alternate_name_1', models.CharField(max_length=100, null=True, blank=True)),
                ('alternate_name_2', models.CharField(max_length=100, null=True, blank=True)),
                ('alternate_name_3', models.CharField(max_length=100, null=True, blank=True)),
                ('description', models.CharField(max_length=500)),
            ],
            options={
                'verbose_name': 'projet',
                'verbose_name_plural': 'projets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SLA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rto', models.IntegerField()),
                ('rpo', models.IntegerField()),
                ('avalability', models.FloatField()),
                ('open_at', models.TimeField()),
                ('closes_at', models.TimeField()),
            ],
            options={
                'verbose_name': 'SLA',
                'verbose_name_plural': 'SLA',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mageparam',
            unique_together=set([('key', 'app', 'model', 'axis1')]),
        ),
        migrations.AddField(
            model_name='implementationrelationdescription',
            name='link_type',
            field=models.ForeignKey(to='ref.ImplementationRelationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='implementationrelationdescription',
            name='source',
            field=models.ForeignKey(related_name='target_set', verbose_name=b'type source', to='ref.ImplementationDescription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='implementationrelationdescription',
            name='target',
            field=models.ForeignKey(related_name='is_targeted_by_set', verbose_name='type cible', to='ref.ImplementationDescription'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='implementationrelationdescription',
            unique_together=set([('name', 'source')]),
        ),
        migrations.AlterUniqueTogether(
            name='implementationfielddescription',
            unique_together=set([('name', 'description')]),
        ),
        migrations.AddField(
            model_name='implementationdescription',
            name='relationships',
            field=models.ManyToManyField(to='ref.ImplementationDescription', through='ref.ImplementationRelationDescription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='implementationcomputedfielddescription',
            name='description',
            field=models.ForeignKey(related_name='computed_field_set', verbose_name='impl\xe9mentation m\xe8re', to='ref.ImplementationDescription'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='implementationcomputedfielddescription',
            unique_together=set([('name', 'description')]),
        ),
        migrations.AddField(
            model_name='environmenttype',
            name='sla',
            field=models.ForeignKey(blank=True, to='ref.SLA', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='project',
            field=models.ForeignKey(blank=True, to='ref.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='typology',
            field=models.ForeignKey(to='ref.EnvironmentType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conventioncounter',
            name='scope_environment',
            field=models.ForeignKey(default=None, blank=True, to='ref.Environment', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conventioncounter',
            name='scope_project',
            field=models.ForeignKey(default=None, blank=True, to='ref.Project', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conventioncounter',
            name='scope_type',
            field=models.ForeignKey(default=None, blank=True, to='ref.ImplementationDescription', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancerelation',
            name='field',
            field=models.ForeignKey(related_name='field_set', verbose_name='champ impl\xe9ment\xe9', to='ref.ImplementationRelationDescription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancerelation',
            name='source',
            field=models.ForeignKey(related_name='rel_target_set', verbose_name=b'instance source', to='ref.ComponentInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancerelation',
            name='target',
            field=models.ForeignKey(related_name='rel_targeted_by_set', verbose_name=b'instance cible', to='ref.ComponentInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancefield',
            name='field',
            field=models.ForeignKey(verbose_name='champ impl\xe9ment\xe9', to='ref.ImplementationFieldDescription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancefield',
            name='instance',
            field=models.ForeignKey(related_name='field_set', verbose_name='instance de composant', to='ref.ComponentInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='description',
            field=models.ForeignKey(related_name='instance_set', verbose_name="d\xe9crit par l'impl\xe9mentation", to='ref.ImplementationDescription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='environments',
            field=models.ManyToManyField(related_name='component_instances', null=True, verbose_name=b'environnements ', to='ref.Environment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='instanciates',
            field=models.ForeignKey(related_name='instances', verbose_name='impl\xe9mentation de ', blank=True, to='ref.ComponentImplementationClass', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='relationships',
            field=models.ManyToManyField(related_name='reverse_relationships', verbose_name=b'relations', through='ref.ComponentInstanceRelation', to='ref.ComponentInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentimplementationclass',
            name='implements',
            field=models.ForeignKey(related_name='implemented_by', verbose_name='composant logique impl\xe9ment\xe9', to='ref.LogicalComponent'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentimplementationclass',
            name='sla',
            field=models.ForeignKey(blank=True, to='ref.SLA', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentimplementationclass',
            name='technical_description',
            field=models.ForeignKey(related_name='cic_set', verbose_name='description technique', to='ref.ImplementationDescription'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='project',
            field=models.ForeignKey(related_name='applications', blank=True, to='ref.Project', null=True),
            preserve_default=True,
        ),
    ]
