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
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='imovel', null=True)

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


    def tipos_transacao(self):
        return self.imovel.get_tipos_transacao()
    
    def get_formas_pagamento(self, transacao):
        return transacao.get_formas_pagamento()


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


class AssinaturaContratoColumn(AbstractKanbanColumn):
    """Coluna específica para Assinatura do Contrato."""

    # Data da assinatura do contrato
    data_assinatura = models.DateField(blank=True, null=True, help_text="Data da assinatura do contrato")
    
    # Campo para anexar o contrato assinado
    contrato_assinado = models.FileField(upload_to='contratos/', blank=True, null=True, help_text="Anexe o contrato assinado")
    
    # Partes envolvidas no contrato (assumindo que temos um modelo de Pessoa para isso)
    partes_envolvidas = models.ManyToManyField(Pessoa, related_name='contratos_envolvidos', help_text="Partes envolvidas na assinatura do contrato")

    # Prazo para conclusão da assinatura
    prazo_assinatura = models.DateTimeField(help_text="Prazo para a assinatura do contrato")

    def verificar_prazo_assinatura(self):
        """Verifica o status do prazo para assinatura e ajusta a cor do cartão."""
        if timezone.now() > self.prazo_assinatura:
            return '#FF0000'  # Vermelho se o prazo passou
        dias_restantes = (self.prazo_assinatura - timezone.now()).days
        if dias_restantes <= 1:
            return '#FFFF00'  # Amarelo se o prazo está próximo
        return '#00FF00'  # Verde se ainda está dentro do prazo

    def anexar_contrato(self, contrato):
        """Anexa o contrato assinado e notifica as partes envolvidas."""
        if not contrato:
            raise ValueError("É necessário anexar o contrato.")
        self.contrato_assinado = contrato
        self.save()
        self.notificar_partes()

    def notificar_partes(self):
        """Envia notificações automáticas para as partes envolvidas com o contrato anexado."""
        for parte in self.partes_envolvidas.all():
            # Enviar email ou notificação para a parte
            # Exemplo: send_email(parte.email, assunto="Contrato assinado", mensagem="Contrato anexado.", anexo=self.contrato_assinado)
            print(f"Notificação enviada para {parte.nome}")

    def mover_para_fechado(self, kanban_card):
        """Move o cartão para a coluna Fechado quando o contrato for assinado."""
        # Verificar se o contrato foi anexado
        if not self.contrato_assinado:
            raise ValueError("O contrato precisa ser assinado antes de mover para a coluna Fechado.")
        # Atualizar o status e mover o cartão
        kanban_card.mover_para_proxima_coluna('Fechado')

    def __str__(self):
        return f"Coluna: {self.nome} - Assinatura do Contrato"
    

class ReprovadoColumn(AbstractKanbanColumn):
    """Coluna específica para Reprovado."""

    # Motivo da reprovação
    motivo_reprovacao = models.TextField(help_text="Motivo detalhado da reprovação do lead")

    # Data de reprovação para controle
    data_reprovacao = models.DateTimeField(auto_now_add=True)

    def registrar_reprovacao(self, motivo):
        """Registra o motivo da reprovação e a data."""
        if not motivo:
            raise ValueError("O motivo da reprovação não pode estar vazio.")
        self.motivo_reprovacao = motivo
        self.data_reprovacao = timezone.now()
        self.save()

    def mover_para_reprovado(self, kanban_card):
        """Move o cartão para a coluna Reprovado com a razão detalhada."""
        # Verifica se o motivo da reprovação está preenchido
        if not self.motivo_reprovacao:
            raise ValueError("O motivo da reprovação precisa ser registrado.")
        
        # Atualiza o status do cartão e move para a coluna 'Reprovado'
        kanban_card.mover_para_proxima_coluna('Reprovado')

    def __str__(self):
        return f"Coluna: {self.nome} - Reprovado"
    

class ReprovadoColumn(AbstractKanbanColumn):
    """Coluna específica para Reprovado."""

    # Motivo da reprovação
    motivo_reprovacao = models.TextField(help_text="Motivo detalhado da reprovação do lead")

    # Data de reprovação para controle
    data_reprovacao = models.DateTimeField(auto_now_add=True)

    def registrar_reprovacao(self, motivo):
        """Registra o motivo da reprovação e a data."""
        if not motivo:
            raise ValueError("O motivo da reprovação não pode estar vazio.")
        self.motivo_reprovacao = motivo
        self.data_reprovacao = timezone.now()
        self.save()

    def mover_para_reprovado(self, kanban_card):
        """Move o cartão para a coluna Reprovado com a razão detalhada."""
        # Verifica se o motivo da reprovação está preenchido
        if not self.motivo_reprovacao:
            raise ValueError("O motivo da reprovação precisa ser registrado.")
        
        # Atualiza o status do cartão e move para a coluna 'Reprovado'
        kanban_card.mover_para_proxima_coluna('Reprovado')

    def __str__(self):
        return f"Coluna: {self.nome} - Reprovado"
    

class InativosColumn(AbstractKanbanColumn):
    """Coluna específica para leads inativos."""

    # Motivo da inatividade
    motivo_inatividade = models.TextField(help_text="Motivo pelo qual o lead ficou inativo")

    # Última ação realizada antes da inatividade
    ultima_acao_realizada = models.TextField(blank=True, null=True, help_text="Última ação realizada no lead")

    # Indica se o lead é recuperável ou arquivado permanentemente
    reativacao_possivel = models.BooleanField(default=True, help_text="Define se o lead pode ser reativado no futuro")

    # Data de inatividade para controle
    data_inatividade = models.DateTimeField(auto_now_add=True)

    def verificar_inatividade(self):
        """Verifica se o lead atingiu o limite de inatividade para ser arquivado."""
        dias_inatividade = (timezone.now() - self.data_inatividade).days
        if dias_inatividade >= 30:
            self.reativacao_possivel = False  # Arquivar como não recuperável após 30 dias
            self.save()
            return '#800080'  # Roxo para inativos arquivados
        elif dias_inatividade >= 20:
            return '#800080'  # Roxo para leads que estão há mais de 20 dias inativos
        return '#00FF00'  # Verde se ainda não está inativo

    def classificar_reativacao(self, reativavel=True):
        """Define se o lead é recuperável ou arquivado permanentemente."""
        self.reativacao_possivel = reativavel
        self.save()

    def __str__(self):
        return f"Coluna: {self.nome} - Inativos"


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


