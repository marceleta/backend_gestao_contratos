from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Estado(models.Model):
    """
    Representa um estado do Brasil, contendo uma sigla e um nome.
    """
    sigla = models.CharField(max_length=2, unique=True)
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Estados"


class Telefone(models.Model):
    """
    Representa um número de telefone associado a uma pessoa.
    Usa GenericForeignKey para associar o telefone a qualquer modelo que herde de Pessoa.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    pessoa = GenericForeignKey('content_type', 'object_id')
    numero = models.CharField(max_length=20)
    tipo = models.CharField(
        max_length=20,
        choices=[('Residencial', 'Residencial'), ('Celular', 'Celular'), ('Comercial', 'Comercial')],
        default='Celular'
    )

    def __str__(self):
        return f"{self.numero} ({self.tipo})"

class Pessoa(models.Model):
    """
    Classe base abstrata para armazenar informações comuns de pessoas,
    como nome, CPF, telefone, email, endereço, etc.
    """
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    identidade = models.CharField(max_length=20, default='')
    orgao_expeditor = models.CharField(max_length=100, default='')
    email = models.EmailField(unique=True)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    cep = models.CharField(max_length=10)
    nacionalidade = models.CharField(max_length=100)
    data_nascimento = models.DateField(default='2000-01-01')
    estado_civil = models.CharField(
        max_length=20,
        choices=[('Solteiro(a)', 'Solteiro(a)'), ('Casado(a)', 'Casado(a)'), ('Divorciado(a)', 'Divorciado(a)'), ('Viúvo(a)', 'Viúvo(a)')],
        default='Solteiro(a)'
    )
    preferencia_comunicacao = models.CharField(
        max_length=50,
        choices=[('Email', 'Email'), ('Telefone', 'Telefone'), ('WhatsApp', 'WhatsApp')],
        default='Whatsapp'
    )

    telefones = GenericRelation(Telefone)

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome