# Generated by Django 3.2.5 on 2021-07-14 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ref', '0002_post_python3_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='environment',
            name='show_sensitive_data',
            field=models.BooleanField(blank=True, choices=[(None, 'défini par la typologie'), (False, 'cacher'), (True, 'montrer')], null=True, verbose_name='afficher les informations sensibles'),
        ),
    ]
