from django.db import models
from usuario.models import Usuario
from imovel.models import Imovel
from datetime import timedelta
from django.utils import timezone 

class Lead(models.Model):
    ETAPA_NOVO = 'novo'
    ETAPA_VISITA = 'visita_imovel'
    ETAPA_DOCUMENTACAO = 'documentacao'
    ETAPA_ANALISE_CREDITO = 'analise_credito'
    ETAPA_APROVADO = 'aprovado'
    ETAPA_REPROVADO = 'reprovado'
    ETAPA_CONTRATO_ASSINADO = 'contrato_assinado'
    
    ETAPA_CHOICES = [
        (ETAPA_NOVO, 'Novo'),
        (ETAPA_VISITA, 'Visita Imóvel'),
        (ETAPA_DOCUMENTACAO, 'Documentação'),
        (ETAPA_ANALISE_CREDITO, 'Análise de Crédito'),
        (ETAPA_APROVADO, 'Aprovado'),
        (ETAPA_REPROVADO, 'Reprovado'),
        (ETAPA_CONTRATO_ASSINADO, 'Contrato Assinado'),
    ]

    AVALIACAO_FRIO = 'frio'
    AVALIACAO_MORNO = 'morno'
    AVALIACAO_QUENTE = 'quente'

    AVALIACAO_CHOICES = [
        (AVALIACAO_FRIO, 'Frio'),
        (AVALIACAO_MORNO, 'Morno'),
        (AVALIACAO_QUENTE, 'Quente'),
    ]

    nome = models.CharField(max_length=255)
    contato = models.CharField(max_length=255)
    email = models.EmailField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    etapa_kanban = models.CharField(max_length=50, choices=ETAPA_CHOICES, default=ETAPA_NOVO)
    avaliacao = models.CharField(max_length=50, choices=AVALIACAO_CHOICES, 
                                 null=True, blank=True,
                                 default=AVALIACAO_FRIO)
    imovel_interesse = models.ForeignKey(Imovel, on_delete=models.CASCADE)
    consultor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    arquivado = models.BooleanField(default=False)

    @classmethod
    def arquivar_leads_antigos():
        prazo = timezone.now() - timedelta(days=30)
        leads = Lead.objects.filter(data_criacao__lt=prazo, arquivado=False)
        for lead in leads:
            lead.arquivar()

    def arquivar(self):
        self.arquivado = True
        self.save()

    def __str__(self):
        return f'{self.nome} - {self.imovel_interesse} - {self.avaliacao}'
    

class HistoricoEtapaKanban(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    etapa_anterior = models.CharField(max_length=50)
    etapa_atual = models.CharField(max_length=50)
    data_alteracao = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.lead.nome} - {self.etapa_atual}'


