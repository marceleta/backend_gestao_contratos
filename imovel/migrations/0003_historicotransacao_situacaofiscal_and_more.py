# Generated by Django 5.1 on 2024-09-05 11:04

import django.db.models.deletion
import django.utils.timezone
import imovel.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('imovel', '0002_imovel_ano_construcao_imovel_area_total_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoTransacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_transacao', models.CharField(choices=[('venda', 'Venda'), ('aluguel', 'Aluguel'), ('permuta', 'Permuta'), ('arrendamento', 'Arrendamento'), ('financiamento', 'Financiamento Imobiliário'), ('leasing', 'Leasing Habitacional')], max_length=13)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data_transacao', models.DateField()),
                ('detalhes', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SituacaoFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('regular', 'Imóvel Regular'), ('iptu_atrasado', 'IPTU Atrasado'), ('taxa_servico_pendente', 'Taxas de Serviço Pendentes'), ('cnd_disponivel', 'Certidão Negativa de Débitos'), ('cpen_disponivel', 'Certidão Positiva com Efeito de Negativa'), ('condominio_pendente', 'Débitos de Condomínio'), ('itbi_pendente', 'ITBI Pendentes')], max_length=50)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_referencia', models.DateField(blank=True, null=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='imovel',
            name='certidoes_licencas',
        ),
        migrations.RemoveField(
            model_name='imovel',
            name='situacao_fiscal',
        ),
        migrations.AddField(
            model_name='imovel',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='imovel',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='imovel',
            name='status',
            field=models.CharField(choices=[('disponivel', 'Disponível'), ('indisponivel', 'Indisponível'), ('em_construcao', 'Em Construção'), ('vendido', 'Vendido')], default='disponivel', max_length=20),
        ),
        migrations.AddField(
            model_name='imovel',
            name='tipo_construcao',
            field=models.CharField(choices=[('novo', 'Novo'), ('usado', 'Usado')], default='novo', max_length=5),
        ),
        migrations.AddField(
            model_name='transacaoimovel',
            name='comissao',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Comissão em %', max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='imovel',
            name='cep',
            field=models.CharField(default='', max_length=10, validators=[imovel.models.Imovel.validate_cep]),
        ),
        migrations.AlterField(
            model_name='imovel',
            name='data_cadastro',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='imovel',
            name='tipo_imovel',
            field=models.CharField(choices=[('casa', 'Casa'), ('apartamento', 'Apartamento'), ('comercial', 'Sala Comercial'), ('terreno', 'Terreno'), ('chacara', 'Chácara'), ('sobrado', 'Sobrado'), ('bangalo', 'Bangalô'), ('edicula', 'Edícula'), ('loft', 'Loft'), ('flat', 'Flat'), ('studio', 'Studio')], default=('casa', 'Casa'), max_length=20),
        ),
        migrations.AlterField(
            model_name='transacaoimovel',
            name='tipo_transacao',
            field=models.CharField(choices=[('venda', 'Venda'), ('aluguel', 'Aluguel'), ('permuta', 'Permuta'), ('arrendamento', 'Arrendamento'), ('financiamento', 'Financiamento Imobiliário'), ('leasing', 'Leasing Habitacional')], max_length=20),
        ),
        migrations.AddIndex(
            model_name='imovel',
            index=models.Index(fields=['nome'], name='imovel_imov_nome_904ea0_idx'),
        ),
        migrations.AddField(
            model_name='historicotransacao',
            name='imovel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='imovel.imovel'),
        ),
        migrations.AddField(
            model_name='situacaofiscal',
            name='imovel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='situacoes_fiscais', to='imovel.imovel'),
        ),
    ]
