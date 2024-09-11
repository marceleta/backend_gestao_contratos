from django.db import models
from django.utils import timezone
from imovel.models import Imovel
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class AbstractKanbanColumn(models.Model):
    nome = models.CharField(max_length=100)  # Nome da coluna
    posicao = models.PositiveIntegerField()  # Posição no fluxo do Kanban
    prazo_alerta = models.PositiveIntegerField(default=3)  # Prazo em horas para alertar sobre inatividade
    cor_inicial = models.CharField(max_length=7, default='#00FF00')  # Cor inicial (verde)
    cor_alerta = models.CharField(max_length=7, default='#FF0000')  # Cor final (vermelho)
    usa_prazo = models.BooleanField(default=False)  # Define se a coluna utiliza um prazo

    class Meta:
        abstract = True

    def verificar_prazo(self, data_prazo):
        """Verifica e altera a cor do cartão com base no prazo em horas."""
        horas_passadas = (timezone.now() - data_prazo).total_seconds() / 3600  # Convertendo segundos em horas
        if data_prazo and horas_passadas > self.prazo_alerta:
            return self.cor_alerta  # Vermelho se o prazo expirou
        elif data_prazo and horas_passadas > (self.prazo_alerta / 2):  
            return '#FFFF00'  # Amarelo se o prazo está próximo
        else:
            return self.cor_inicial  # Verde se ainda está dentro do prazo
        

class ContatoInicialColumn(AbstractKanbanColumn):
    """Coluna específica para Contato Inicial."""

    ORIGEM_LEAD = [
        ('landing_page', 'Landing Page'),
        ('contato_offline', 'Contato Offline'),
        ('chatbot', 'Chatbot')
    ]
    
    # Campo adicional para armazenar a origem do lead
    origem_lead = models.CharField(max_length=40, blank=True, null=True, default='contato_offline', 
                                   help_text="Imóvel de interesse do lead, se houver", choices=ORIGEM_LEAD)
    imovel_interessado = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='imovel')
    
    def verificar_origem(self):
        """Método para verificar e categorizar a origem do lead."""
        if not self.origem_lead:
            raise ValueError("A origem do lead é obrigatória.")
        return True

    
    def __str__(self):
        return f"Coluna: {self.nome} - Contato Inicial"
    


class VisitaImovelColumn(AbstractKanbanColumn):
    """Coluna específica para Visita ao Imóvel."""

    data_visita = models.DateTimeField(help_text="Data e hora da visita agendada")
    observacoes = models.TextField(blank=True, null=True, help_text="Observações sobre a visita")
    visita_realizada = models.BooleanField(default=False, help_text="Indica se a visita foi realizada")
    reagendada = models.BooleanField(default=False, help_text="Indica se a visita foi reagendada")

    def verificar_data_visita(self):
        """Verifica se a data da visita foi marcada."""
        if not self.data_visita:
            raise ValueError("A data e hora da visita são obrigatórias.")
        return True

    def marcar_visita_realizada(self, observacoes):
        """Marca a visita como realizada e solicita observações sobre o Lead."""
        if not observacoes:
            raise ValueError("As observações são obrigatórias ao marcar uma visita como realizada.")
        self.visita_realizada = True
        self.observacoes = observacoes
        self.save()

    def reagendar_visita(self, nova_data):
        """Permite que o usuário reagende a visita sem perder o histórico."""
        if nova_data <= timezone.now():
            raise ValueError("A nova data da visita deve ser no futuro.")
        self.reagendada = True
        self.data_visita = nova_data
        self.save()

    def verificar_prazo_alerta_visita(self):
        """Verifica o tempo restante para a visita e muda a cor do cartão."""
        horas_restantes = (self.data_visita - timezone.now()).total_seconds() / 3600
        if horas_restantes <= 1:
            return '#FF0000'  # Vermelho quando falta menos de uma hora
        elif horas_restantes <= 3:
            return '#FFFF00'  # Amarelo quando falta menos de três horas
        else:
            return '#00FF00'  # Verde se ainda está dentro do prazo

    def __str__(self):
        return f"Coluna: {self.nome} - Visita ao Imóvel"



class NegociacaoColumn(AbstractKanbanColumn):
    """Coluna específica para Negociação."""

    STATUS_NEGOCIACAO = [
        ('em_negociacao', 'Em Negociação'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada')
    ]

    TIPO_GARANTIA = [
        ('fiador', 'Fiador'),
        ('deposito_caucao', 'Depósito Caução'),
        ('seguro_fianca', 'Seguro Fiança'),
        ('titulo_capitalizacao', 'Título de Capitalização'),
        ('caucao_imovel', 'Caução de Imóvel')
    ]
    
    # Campos específicos para a negociação
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor final da negociação")
    tipo_garantia = models.CharField(max_length=50, blank=True, null=True, choices=TIPO_GARANTIA, default='fiador', help_text="Tipo de garantia: fiador, depósito, etc.")
    prazo_vigencia = models.PositiveIntegerField(blank=True, null=True, help_text="Prazo de vigência do contrato em meses")
    condicoes_especiais = models.TextField(blank=True, null=True, help_text="Condições especiais do contrato")
    metodo_pagamento = models.CharField(max_length=100, blank=True, null=True, help_text="Método de pagamento")
    data_prevista_fechamento = models.DateField(blank=True, null=True, help_text="Data prevista de fechamento da negociação")
    status_negociacao = models.CharField(max_length=20, choices=STATUS_NEGOCIACAO, default='em_negociacao', help_text="Status da negociação")
    observacoes = models.TextField(blank=True, null=True, help_text="Observações sobre a negociação")

    def verificar_campos_obrigatorios(self):
        """Verifica se todos os campos obrigatórios estão preenchidos para avançar."""
        if not self.valor_final or not self.tipo_garantia or not self.prazo_vigencia or not self.metodo_pagamento:
            return False
        return True


    def registrar_feedback(self, feedback):
        """Registra o feedback do lead durante a negociação."""
        if not feedback:
            raise ValueError("O feedback não pode estar vazio.")
        self.observacoes = feedback
        self.save()

    def __str__(self):
        return f"Coluna: {self.nome} - Negociação"



class DocumentacaoAnaliseCreditoColumn(AbstractKanbanColumn):
    """Coluna específica para Documentação e Análise de Crédito."""

    STATUS_DOCUMENTACAO = [
        ('pendente', 'Pendente'),
        ('completa', 'Completa'),
        ('incompleta', 'Incompleta'),
        ('vencida', 'Vencida')
    ]

    RESULTADO_ANALISE_CREDITO = [
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
        ('em_analise', 'Em Análise')
    ]

    # Campos relacionados à documentação
    documentos_anexados = models.FileField(upload_to='documentos/', blank=True, null=True, help_text="Documentos anexados para análise")
    status_documentacao = models.CharField(max_length=20, choices=STATUS_DOCUMENTACAO, default='pendente', help_text="Status da documentação")
    observacoes_documentacao = models.TextField(blank=True, null=True, help_text="Observações sobre os documentos")
    resultado_analise_credito = models.CharField(max_length=20, choices=RESULTADO_ANALISE_CREDITO, default='em_analise', help_text="Resultado da análise de crédito")
    prazo_entrega_documentos = models.DateTimeField(help_text="Prazo para a entrega dos documentos")

    def anexar_documentos(self, documentos):
        """Anexa os documentos para análise e altera o status."""
        if not documentos:
            raise ValueError("É necessário anexar os documentos.")
        self.documentos_anexados = documentos
        self.status_documentacao = 'completa'
        self.save()

    def realizar_analise_credito(self, resultado):
        """Registra o resultado da análise de crédito."""
        if resultado not in ['aprovado', 'reprovado']:
            raise ValueError("Resultado da análise de crédito inválido.")
        self.resultado_analise_credito = resultado
        self.save()

    def __str__(self):
        return f"Coluna: {self.nome} - Documentação e Análise de Crédito" 

class KanbanCard(models.Model):
    lead_nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    data_prazo = models.DateTimeField(null=True, blank=True)
    cor_atual = models.CharField(max_length=7, default='#00FF00')  # Cor inicial (verde)

    # Campos necessários para usar GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def atualizar_cor(self):
        """Atualiza a cor do cartão com base no prazo da coluna atual."""
        if hasattr(self.content_object, 'verificar_prazo'):
            self.cor_atual = self.content_object.verificar_prazo(self.data_criacao)
            self.save()

    def mover_para_proxima_coluna(self, nova_coluna):
        """Move o cartão para a próxima coluna e atualiza a cor."""        
        if not isinstance(nova_coluna, AbstractKanbanColumn):
            raise ValidationError("A nova coluna deve herdar de AbstractKanbanColumn.")
        
        # Atualiza o objeto da coluna (content_object) para a nova coluna
        self.content_object = nova_coluna
        self.atualizar_cor()  # Atualiza a cor baseada na nova coluna
        self.save()

    def __str__(self):
        return f"Lead: {self.lead_nome} na Coluna: {self.content_object}"


