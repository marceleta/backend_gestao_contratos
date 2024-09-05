from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class SituacaoFiscal(models.Model):
    SITUACAO_FISCAL_CHOICES = [
        ('regular', 'Imóvel Regular'),
        ('iptu_atrasado', 'IPTU Atrasado'),
        ('taxa_servico_pendente', 'Taxas de Serviço Pendentes'),
        ('cnd_disponivel', 'Certidão Negativa de Débitos'),
        ('cpen_disponivel', 'Certidão Positiva com Efeito de Negativa'),
        ('condominio_pendente', 'Débitos de Condomínio'),
        ('itbi_pendente', 'ITBI Pendentes'),
    ]

    tipo = models.CharField(max_length=50, choices=SITUACAO_FISCAL_CHOICES)
    descricao = models.TextField(null=True, blank=True)
    data_referencia = models.DateField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)


    imovel = models.ForeignKey('Imovel', on_delete=models.CASCADE, related_name='situacoes_fiscais')  # Relacionamento com o imóvel

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.imovel.nome}"


class Imovel(models.Model):

    class Meta:
        indexes = [models.Index(fields=['nome']),
    ]
    # Informações Básicas
    nome = models.CharField(max_length=255, default="")
    endereco = models.CharField(max_length=255, default="")
    bairro = models.CharField(max_length=100, default="")
    cidade = models.CharField(max_length=100, default="")
    estado = models.CharField(max_length=50, default="")
    
    area_total = models.DecimalField(max_digits=7, decimal_places=2, help_text="Área total em metros quadrados", default=0)
    area_util = models.DecimalField(max_digits=7, decimal_places=2, help_text="Área útil em metros quadrados", default=0)
    
    # Detalhes do Imóvel
    TIPO_IMOVEL_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('comercial', 'Sala Comercial'),
        ('terreno', 'Terreno'),
        ('chacara', 'Chácara'),
        ('sobrado', 'Sobrado'),
        ('bangalo', 'Bangalô'),
        ('edicula', 'Edícula'),
        ('loft', 'Loft'),
        ('flat', 'Flat'),
        ('studio', 'Studio'),
    ]
    tipo_imovel = models.CharField(max_length=20, choices=TIPO_IMOVEL_CHOICES, default=TIPO_IMOVEL_CHOICES[0])
    num_quartos = models.IntegerField(default=0)
    num_banheiros = models.IntegerField(default=0)
    num_vagas_garagem = models.IntegerField(default=0)
    ano_construcao = models.IntegerField(null=True, blank=True)
    caracteristicas_adicionais = models.TextField(null=True, blank=True, help_text="Ex: Piscina, churrasqueira, varanda")

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('indisponivel', 'Indisponível'),
        ('em_construcao', 'Em Construção'),
        ('vendido', 'Vendido'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')

    TIPO_CONSTRUCAO_CHOICES = [
        ('novo', 'Novo'),
        ('usado', 'Usado'),
    ]
    tipo_construcao = models.CharField(max_length=5, choices=TIPO_CONSTRUCAO_CHOICES, default='novo')


    # Documentação e Legalidade
    numero_registro = models.CharField(max_length=50, unique=True, help_text="Número de matrícula no cartório de imóveis", default="")
    
    # Status de Disponibilidade
    disponibilidade = models.BooleanField(default=True, help_text="Indica se o imóvel está disponível")
    data_cadastro = models.DateTimeField(default=timezone.now)

    def validate_cep(value):
        if len(value) != 9 or not value[:5].isdigit() or not value[6:].isdigit() or value[5] != '-':
            raise ValidationError("CEP deve estar no formato XXXXX-XXX.")
        
    cep = models.CharField(max_length=10, validators=[validate_cep], default="")

    def __str__(self):
        return f"{self.nome} - {self.cidade}/{self.estado}"
    

class TransacaoImovel(models.Model):
    TIPO_TRANSACAO_CHOICES = [
        ('venda', 'Venda'),
        ('aluguel', 'Aluguel'),
        ('permuta', 'Permuta'),
        ('arrendamento', 'Arrendamento'),
        ('financiamento', 'Financiamento Imobiliário'),
        ('leasing', 'Leasing Habitacional'),
    ]

    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='transacoes')

    comissao = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Comissão em %")

    tipo_transacao = models.CharField(max_length=20, choices=TIPO_TRANSACAO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    condicoes_pagamento = models.TextField(null=True, blank=True, help_text="Detalhes sobre financiamento, entrada, parcelamento")
    data_disponibilidade = models.DateField()

    def __str__(self):
        return f"{self.imovel.nome} - {self.tipo_transacao}"
    

class HistoricoTransacao(models.Model):
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE)
    tipo_transacao = models.CharField(max_length=13, choices=TransacaoImovel.TIPO_TRANSACAO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_transacao = models.DateField()
    detalhes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.imovel.nome} - {self.campo_modificado} - {self.data_modificacao}"


