# Generated by Django 5.1 on 2024-10-31 17:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sigla', models.CharField(max_length=2, unique=True)),
                ('nome', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Estados',
            },
        ),
        migrations.CreateModel(
            name='PessoaFisica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefone', models.CharField(max_length=20)),
                ('endereco', models.CharField(max_length=255)),
                ('bairro', models.CharField(max_length=100)),
                ('cidade', models.CharField(max_length=100)),
                ('cep', models.CharField(max_length=10)),
                ('preferencia_comunicacao', models.CharField(choices=[('Email', 'Email'), ('Telefone', 'Telefone'), ('WhatsApp', 'WhatsApp')], default='Whatsapp', max_length=50)),
                ('cpf', models.CharField(max_length=14, unique=True)),
                ('identidade', models.CharField(max_length=20, unique=True)),
                ('orgao_expeditor', models.CharField(max_length=100)),
                ('cnh', models.CharField(blank=True, max_length=20, null=True)),
                ('orgao_expeditor_cnh', models.CharField(blank=True, max_length=100, null=True)),
                ('data_nascimento', models.DateField()),
                ('estado_civil', models.CharField(choices=[('Solteiro(a)', 'Solteiro(a)'), ('Casado(a)', 'Casado(a)'), ('Divorciado(a)', 'Divorciado(a)'), ('Viúvo(a)', 'Viúvo(a)')], default='Solteiro(a)', max_length=20)),
                ('nacionalidade', models.CharField(max_length=100)),
                ('profissao', models.CharField(blank=True, max_length=100, null=True)),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.estado')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PessoaJuridica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefone', models.CharField(max_length=20)),
                ('endereco', models.CharField(max_length=255)),
                ('bairro', models.CharField(max_length=100)),
                ('cidade', models.CharField(max_length=100)),
                ('cep', models.CharField(max_length=10)),
                ('preferencia_comunicacao', models.CharField(choices=[('Email', 'Email'), ('Telefone', 'Telefone'), ('WhatsApp', 'WhatsApp')], default='Whatsapp', max_length=50)),
                ('cnpj', models.CharField(max_length=18, unique=True)),
                ('data_fundacao', models.DateField()),
                ('nome_fantasia', models.CharField(blank=True, max_length=255, null=True)),
                ('data_abertura', models.DateField(blank=True, null=True)),
                ('inscricao_estadual', models.CharField(blank=True, max_length=100, null=True)),
                ('natureza_juridica', models.CharField(blank=True, max_length=100, null=True)),
                ('atividade_principal_cnae', models.CharField(blank=True, max_length=100, null=True)),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.estado')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Representante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cargo', models.CharField(max_length=100)),
                ('nivel_autoridade', models.CharField(choices=[('Diretor', 'Diretor'), ('Gerente', 'Gerente'), ('Supervisor', 'Supervisor')], default='Supervisor', max_length=50)),
                ('pessoa_fisica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='representante', to='core.pessoafisica')),
                ('pessoa_juridica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='representantes', to='core.pessoajuridica')),
            ],
        ),
        migrations.CreateModel(
            name='Telefone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20)),
                ('tipo', models.CharField(choices=[('Residencial', 'Residencial'), ('Celular', 'Celular'), ('Comercial', 'Comercial'), ('Whatsapp', 'Whatsapp')], default='Whatsapp', max_length=20)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
    ]
