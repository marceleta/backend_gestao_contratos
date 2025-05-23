# Generated by Django 5.1 on 2024-12-04 12:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imovel', '0001_initial'),
        ('kanban', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kanbancard',
            name='contato',
            field=models.JSONField(blank=True, default=dict, help_text='Informações de contato do lead, como telefone, WhatsApp, e e-mail', null=True),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='contrato_assinado',
            field=models.TextField(blank=True, help_text='Contrato assinado anexado'),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='data_assinatura',
            field=models.DateTimeField(blank=True, help_text='Data da assinatura do contrato', null=True),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='data_visita',
            field=models.DateTimeField(blank=True, help_text='Data e hora da visita agendada', null=True),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='documentos_anexados',
            field=models.TextField(blank=True, help_text='Documentos anexados para análise'),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='imovel',
            field=models.ForeignKey(blank=True, help_text='Imovel que o contato está interessado', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='imovel', to='imovel.imovel'),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='metodo_pagamento',
            field=models.CharField(blank=True, help_text='Método de pagamento', max_length=100),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='observacoes_visita',
            field=models.TextField(blank=True, help_text='Observações sobre a visita'),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='prazo_vigencia',
            field=models.CharField(blank=True, help_text='Prazo de vigência do contrato', max_length=100),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='resultado_analise_credito',
            field=models.CharField(blank=True, help_text='Resultado da análise de crédito', max_length=100),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='status_documentacao',
            field=models.CharField(blank=True, help_text='Status da documentação', max_length=100),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='tipo_garantia',
            field=models.CharField(blank=True, help_text='Tipo de garantia', max_length=100),
        ),
        migrations.AddField(
            model_name='kanbancard',
            name='valor_final',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Valor final da negociação', max_digits=10, null=True),
        ),
    ]
