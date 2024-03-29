# Generated by Django 3.2.12 on 2022-10-01 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ref', '0004_auto_20221001_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='ref.project'),
        ),
        migrations.AlterField(
            model_name='environment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ref.project'),
        ),
    ]
