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
    numero = models.CharField(max_length=20)
    tipo = models.CharField(
        max_length=20,
        choices=[('Residencial', 'Residencial'), ('Celular', 'Celular'), ('Comercial', 'Comercial'), ("Whatsapp", "Whatsapp")],
        default='Whatsapp'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.numero} ({self.tipo})"
    

class Endereco(models.Model):
    """
    Representa um endereço que pode estar associado a diferentes tipos de entidades.
    """
    tipo_endereco = models.CharField(max_length=50, null=True, blank=True)
    rua = models.CharField(max_length=255)
    numero = models.CharField(max_length=50)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    cep = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.bairro}, {self.cidade}"


class Pessoa(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    preferencia_comunicacao = models.CharField(
        max_length=50,
        choices=[('Email', 'Email'), ('Telefone', 'Telefone'), ('WhatsApp', 'WhatsApp')],
        default='Whatsapp'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome
    
class PessoaFisica(Pessoa):
    cpf = models.CharField(max_length=14, unique=True)
    identidade = models.CharField(max_length=20, unique=True)
    orgao_expeditor = models.CharField(max_length=100)
    cnh = models.CharField(max_length=20, null=True, blank=True)
    orgao_expeditor_cnh = models.CharField(max_length=100, null=True, blank=True)
    data_nascimento = models.DateField()
    estado_civil = models.CharField(
        max_length=20,
        choices=[('Solteiro(a)', 'Solteiro(a)'), ('Casado(a)', 'Casado(a)'), ('Divorciado(a)', 'Divorciado(a)'), ('Viúvo(a)', 'Viúvo(a)')],
        default='Solteiro(a)'
    )
    nacionalidade = models.CharField(max_length=100)
    profissao = models.CharField(max_length=100, null=True, blank=True)
    sexo = models.CharField(
        max_length=10,
        choices=[('Masculino', 'Masculino'), ('Feminino', 'Feminino'), ('Outro', 'Outro')],
        null=True, blank=True
    )
    telefones = GenericRelation(Telefone)
    enderecos = GenericRelation(Endereco)


    def __str__(self):
        return f"{self.nome} (Pessoa Física)"
    

class PessoaJuridica(Pessoa):
    cnpj = models.CharField(max_length=18, unique=True)
    data_fundacao = models.DateField()
    nome_fantasia = models.CharField(max_length=255, null=True, blank=True)
    data_abertura = models.DateField(null=True, blank=True)
    inscricao_estadual = models.CharField(max_length=100, null=True, blank=True)
    natureza_juridica = models.CharField(max_length=100, null=True, blank=True)
    atividade_principal_cnae = models.CharField(max_length=100, null=True, blank=True)
    telefones = GenericRelation(Telefone)
    enderecos = GenericRelation(Endereco)

    def __str__(self):
        return f"{self.nome_fantasia or self.nome} (Pessoa Jurídica)"
    
    
    
class Representante(models.Model):
    pessoa_fisica = models.ForeignKey(PessoaFisica, on_delete=models.CASCADE, related_name='representante')
    pessoa_juridica = models.ForeignKey(PessoaJuridica, on_delete=models.CASCADE, related_name='representantes')
    cargo = models.CharField(max_length=100)
    nivel_autoridade = models.CharField(
        max_length=50,
        choices=[('Diretor', 'Diretor'), ('Gerente', 'Gerente'), ('Supervisor', 'Supervisor')],
        default='Supervisor'
    )

    def __str__(self):
        return f"Representante: {self.pessoa_fisica.nome} ({self.cargo}, {self.nivel_autoridade}) para {self.pessoa_juridica.nome_fantasia or self.pessoa_juridica.nome}"