# Generated by Django 3.2.15 on 2022-10-01 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scm', '0005_auto_20221001_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='installableset',
            name='name',
            field=models.CharField(max_length=40, verbose_name='référence'),
        ),
        migrations.AddConstraint(
            model_name='installableset',
            constraint=models.UniqueConstraint(fields=('name', 'project'), name='is_installableset_uniqueness'),
        ),
    ]