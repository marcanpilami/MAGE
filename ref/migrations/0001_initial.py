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
                ('name', models.CharField(max_length=100, verbose_name=u'code')),
                ('description', models.CharField(max_length=500)),
                ('ref1', models.CharField(max_length=20, null=True, verbose_name='reférence 1', blank=True)),
                ('ref2', models.CharField(max_length=20, null=True, verbose_name='reférence 2', blank=True)),
                ('ref3', models.CharField(max_length=20, null=True, verbose_name='reférence 3', blank=True)),
                ('active', models.BooleanField(default=True, verbose_name='utilisé')),
            ],
            options={
                'verbose_name': 'offre implémentant un composant logique',
                'verbose_name_plural': 'offres implémentant des composants logiques',
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
                ('value', models.CharField(max_length=255, verbose_name=u'valeur', db_index=True)),
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
                ('val', models.IntegerField(default=0, verbose_name=u'valeur courante')),
                ('scope_application', models.ForeignKey(default=None, blank=True, to='ref.Application', null=True, on_delete=models.CASCADE)),
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
                ('name', models.CharField(unique=True, max_length=100, verbose_name=u'Nom')),
                ('buildDate', models.DateField(auto_now_add=True, verbose_name='Date de création')),
                ('destructionDate', models.DateField(null=True, verbose_name='Date de suppression prévue', blank=True)),
                ('description', models.CharField(max_length=500)),
                ('manager', models.CharField(max_length=100, null=True, verbose_name=u'responsable', blank=True)),
                ('template_only', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True, verbose_name='utilisé')),
                ('show_sensitive_data', models.NullBooleanField(verbose_name=u'afficher les informations sensibles')),
                ('managed', models.BooleanField(default=True, verbose_name='administré')),
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
                ('name', models.CharField(unique=True, max_length=100, verbose_name=u'Nom')),
                ('description', models.CharField(max_length=500, verbose_name=u'description')),
                ('short_name', models.CharField(max_length=10, verbose_name=u'code', db_index=True)),
                ('chronological_order', models.IntegerField(default=1, verbose_name="ordre d'affichage")),
                ('default_show_sensitive_data', models.BooleanField(default=False, verbose_name=u'afficher les informations sensibles')),
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
                ('key', models.CharField(max_length=50, verbose_name=u'clef')),
                ('value', models.CharField(max_length=100, verbose_name=u'valeur')),
                ('instance', models.ForeignKey(related_name='parameter_set', to='ref.ComponentInstance', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'paramètre étendu',
                'verbose_name_plural': 'paramètres étendus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImplementationComputedFieldDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=u'nom court du champ')),
                ('label', models.CharField(max_length=150, verbose_name=u'label')),
                ('label_short', models.CharField(help_text='si vide, label sera utilisé', max_length=30, null=True, verbose_name=u'label court', blank=True)),
                ('help_text', models.CharField(max_length=254, null=True, verbose_name=u'aide descriptive du champ', blank=True)),
                ('sensitive', models.BooleanField(default=False, verbose_name=u'sensible')),
                ('pattern', models.CharField(max_length=500, verbose_name=u'chaîne de calcul')),
                ('widget_row', models.PositiveSmallIntegerField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'champ calculé',
                'verbose_name_plural': 'champs calculés',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImplementationDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name=u'nom', db_index=True)),
                ('description', models.CharField(max_length=500, verbose_name=u'description')),
                ('tag', models.CharField(db_index=True, max_length=100, null=True, verbose_name='catégorie', blank=True)),
                ('include_in_default_envt_backup', models.BooleanField(default=False, verbose_name='inclure dans les backups par défaut')),
                ('self_description_pattern', models.CharField(help_text='sera utilisé pour toutes les descriptions par défaut des instances de composant. Utilise les même motifs (patterns) que les champs dynamiques.', max_length=500, verbose_name="motif d'auto description")),
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
                ('name', models.CharField(max_length=100, verbose_name=u'nom court du champ')),
                ('label', models.CharField(max_length=150, verbose_name=u'label')),
                ('label_short', models.CharField(help_text='si vide, label sera utilisé', max_length=30, null=True, verbose_name=u'label court', blank=True)),
                ('help_text', models.CharField(max_length=254, null=True, verbose_name=u'aide descriptive du champ', blank=True)),
                ('sensitive', models.BooleanField(default=False, verbose_name=u'sensible')),
                ('compulsory', models.BooleanField(default=True)),
                ('default', models.CharField(max_length=500, null=True, verbose_name=u'défaut', blank=True)),
                ('datatype', models.CharField(default='str', max_length=20, verbose_name='type', choices=[(u'str', u'chaîne de caractères'), (u'int', u'entier')])),
                ('widget_row', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('description', models.ForeignKey(related_name='field_set', verbose_name=u'implémentation mère', to='ref.ImplementationDescription', on_delete=models.CASCADE)),
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
                ('name', models.CharField(max_length=100, verbose_name=u'nom court du champ')),
                ('label', models.CharField(max_length=150, verbose_name=u'label')),
                ('label_short', models.CharField(help_text=u'si vide, label sera utilisé', max_length=30, null=True, verbose_name=u'label court', blank=True)),
                ('help_text', models.CharField(max_length=254, null=True, verbose_name=u'aide descriptive du champ', blank=True)),
                ('sensitive', models.BooleanField(default=False, verbose_name=u'sensible')),
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
                ('name', models.CharField(max_length=20, verbose_name=u'type relation')),
                ('label', models.CharField(max_length=100, verbose_name=u'label')),
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
                ('url', models.URLField(verbose_name=u'URL cible')),
                ('legend', models.CharField(max_length=100, verbose_name=u'légende du lien')),
                ('color', models.CharField(help_text=u'couleur au format #RRGGBB hexadécimal. Ex: #FF00CC', max_length=7, verbose_name=u'couleur')),
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
                ('name', models.CharField(max_length=100, verbose_name=u'nom')),
                ('description', models.CharField(max_length=500)),
                ('scm_trackable', models.BooleanField(default=True)),
                ('active', models.BooleanField(default=True, verbose_name=u'utilisé')),
                ('ref1', models.CharField(max_length=20, null=True, verbose_name='reférence 1', blank=True)),
                ('ref2', models.CharField(max_length=20, null=True, verbose_name='reférence 2', blank=True)),
                ('ref3', models.CharField(max_length=20, null=True, verbose_name='reférence 3', blank=True)),
                ('application', models.ForeignKey(to='ref.Application', on_delete=models.CASCADE)),
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
                ('key', models.CharField(max_length=30, verbose_name='clé')),
                ('app', models.CharField(max_length=5, verbose_name='application', choices=[(u'crispy_forms', u'crispy_forms'), (u'ref', u'ref'), (u'scm', u'scm'), (u'debug_toolbar', u'debug_toolbar')])),
                ('value', models.CharField(max_length=100, verbose_name='valeur')),
                ('description', models.CharField(max_length=200, null=True, verbose_name='description', blank=True)),
                ('default_value', models.CharField(max_length=100, null=True, verbose_name='valeur par défaut', blank=True)),
                ('axis1', models.CharField(max_length=30, null=True, verbose_name='classification optionnelle', blank=True)),
                ('restricted', models.BooleanField(default=False)),
                ('model', models.ForeignKey(verbose_name='modèle concerné', blank=True, to='contenttypes.ContentType', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['app', 'key'],
                'verbose_name': 'paramètre global',
                'verbose_name_plural': 'paramètres globaux',
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
            field=models.ForeignKey(to='ref.ImplementationRelationType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='implementationrelationdescription',
            name='source',
            field=models.ForeignKey(related_name='target_set', verbose_name=u'type source', to='ref.ImplementationDescription', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='implementationrelationdescription',
            name='target',
            field=models.ForeignKey(related_name='is_targeted_by_set', verbose_name='type cible', to='ref.ImplementationDescription', on_delete=models.CASCADE),
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
            field=models.ForeignKey(related_name='computed_field_set', verbose_name='implémentation mère', to='ref.ImplementationDescription', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='implementationcomputedfielddescription',
            unique_together=set([('name', 'description')]),
        ),
        migrations.AddField(
            model_name='environmenttype',
            name='sla',
            field=models.ForeignKey(blank=True, to='ref.SLA', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='project',
            field=models.ForeignKey(blank=True, to='ref.Project', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='environment',
            name='typology',
            field=models.ForeignKey(to='ref.EnvironmentType', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conventioncounter',
            name='scope_environment',
            field=models.ForeignKey(default=None, blank=True, to='ref.Environment', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conventioncounter',
            name='scope_project',
            field=models.ForeignKey(default=None, blank=True, to='ref.Project', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='conventioncounter',
            name='scope_type',
            field=models.ForeignKey(default=None, blank=True, to='ref.ImplementationDescription', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancerelation',
            name='field',
            field=models.ForeignKey(related_name='field_set', verbose_name='champ implémenté', to='ref.ImplementationRelationDescription', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancerelation',
            name='source',
            field=models.ForeignKey(related_name='rel_target_set', verbose_name=u'instance source', to='ref.ComponentInstance', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancerelation',
            name='target',
            field=models.ForeignKey(related_name='rel_targeted_by_set', verbose_name=u'instance cible', to='ref.ComponentInstance', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancefield',
            name='field',
            field=models.ForeignKey(verbose_name='champ implémenté', to='ref.ImplementationFieldDescription', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstancefield',
            name='instance',
            field=models.ForeignKey(related_name='field_set', verbose_name='instance de composant', to='ref.ComponentInstance', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='description',
            field=models.ForeignKey(related_name='instance_set', verbose_name="décrit par l'implémentation", to='ref.ImplementationDescription', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='environments',
            field=models.ManyToManyField(related_name='component_instances', null=True, verbose_name='environnements ', to='ref.Environment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='instanciates',
            field=models.ForeignKey(related_name='instances', verbose_name='implémentation de ', blank=True, to='ref.ComponentImplementationClass', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentinstance',
            name='relationships',
            field=models.ManyToManyField(related_name='reverse_relationships', verbose_name=u'relations', through='ref.ComponentInstanceRelation', to='ref.ComponentInstance'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentimplementationclass',
            name='implements',
            field=models.ForeignKey(related_name='implemented_by', verbose_name='composant logique implémenté', to='ref.LogicalComponent', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentimplementationclass',
            name='sla',
            field=models.ForeignKey(blank=True, to='ref.SLA', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='componentimplementationclass',
            name='technical_description',
            field=models.ForeignKey(related_name='cic_set', verbose_name='description technique', to='ref.ImplementationDescription', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='project',
            field=models.ForeignKey(related_name='applications', blank=True, to='ref.Project', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
