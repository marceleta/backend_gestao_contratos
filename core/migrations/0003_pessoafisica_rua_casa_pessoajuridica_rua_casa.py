# Generated by Django 5.1 on 2025-02-07 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_pessoafisica_numero_casa_pessoajuridica_numero_casa'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoafisica',
            name='rua_casa',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='pessoajuridica',
            name='rua_casa',
            field=models.CharField(default='', max_length=255),
        ),
    ]
