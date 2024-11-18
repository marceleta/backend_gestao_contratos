from usuario.models import Usuario
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import models
from django.db.models import F, Max


class KanbanCard(models.Model):
    lead_nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(null=True, blank=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    data_prazo = models.DateTimeField(null=True, blank=True)
    cor_atual = models.CharField(max_length=7, default='#00FF00')  # Cor inicial (verde)
    dados_adicionais = models.TextField(blank=True, help_text="Campo para dados dinâmicos adicionais")
    
    # Dados específicos para a coluna Visita ao Imóvel
    data_visita = models.DateTimeField(help_text="Data e hora da visita agendada", null=True, blank=True)
    observacoes_visita = models.TextField(blank=True, null=True, help_text="Observações sobre a visita")
    visita_realizada = models.BooleanField(default=False, help_text="Indica se a visita foi realizada")
    visita_reagendada = models.BooleanField(default=False, help_text="Indica se a visita foi reagendada")

    # Dados específicos para a coluna Negociação
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Valor final da negociação")
    tipo_garantia = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('fiador', 'Fiador'), ('deposito_caucao', 'Depósito Caução'), 
        ('seguro_fianca', 'Seguro Fiança'), ('titulo_capitalizacao', 'Título de Capitalização'), 
        ('caucao_imovel', 'Caução de Imóvel')
    ], help_text="Tipo de garantia")
    prazo_vigencia = models.PositiveIntegerField(blank=True, null=True, help_text="Prazo de vigência do contrato em meses")
    metodo_pagamento = models.CharField(max_length=100, blank=True, null=True, help_text="Método de pagamento")
    status_negociacao = models.CharField(max_length=20, choices=[
        ('em_negociacao', 'Em Negociação'), ('concluida', 'Concluída'), ('cancelada', 'Cancelada')
    ], default='em_negociacao', help_text="Status da negociação")

    # Dados específicos para a coluna Documentação e Análise de Crédito
    documentos_anexados = models.FileField(upload_to='documentos/', blank=True, null=True, help_text="Documentos anexados para análise")
    status_documentacao = models.CharField(max_length=20, choices=[
        ('pendente', 'Pendente'), ('completa', 'Completa'), ('incompleta', 'Incompleta'), ('vencida', 'Vencida')
    ], default='pendente', help_text="Status da documentação")
    resultado_analise_credito = models.CharField(max_length=20, choices=[
        ('aprovado', 'Aprovado'), ('reprovado', 'Reprovado'), ('em_analise', 'Em Análise')
    ], default='em_analise', help_text="Resultado da análise de crédito")

    # Assinatura do Contrato
    data_assinatura = models.DateField(blank=True, null=True, help_text="Data da assinatura do contrato")
    contrato_assinado = models.FileField(upload_to='contratos/', blank=True, null=True, help_text="Anexe o contrato assinado")
    
    # Campos necessários para usar GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def associar_a_coluna(self, coluna):
        if not isinstance(coluna, AbstractKanbanColumn):
            raise ValidationError("A coluna deve ser uma subclasse de AbstractKanbanColumn.")

        # Validação de campos obrigatórios
        coluna.validar_campos(self)

        self.content_type = ContentType.objects.get_for_model(coluna)
        self.object_id = coluna.id
        self.save()

    def atualizar_cor(self):
        """Atualiza a cor do cartão com base no prazo da coluna atual."""
        if hasattr(self.content_object, 'verificar_prazo'):
            self.cor_atual = self.content_object.verificar_prazo(self.data_criacao)
            self.save()

    def __str__(self):
        return f"Lead: {self.lead_nome} na Coluna: {self.content_object}"


class AbstractKanbanColumn(models.Model):
    """Modelo abstrato para colunas do Kanban."""
    nome = models.CharField(max_length=100)
    prazo_alerta = models.PositiveIntegerField(default=3)  # Em horas
    cor_inicial = models.CharField(max_length=7, default='#00FF00')
    cor_alerta = models.CharField(max_length=7, default='#FF0000')

    class Meta:
        abstract = True

    def verificar_prazo(self, data_criacao):
        horas_passadas = (timezone.now() - data_criacao).total_seconds() / 3600
        if horas_passadas > self.prazo_alerta:            
            return self.cor_alerta
        elif horas_passadas > (self.prazo_alerta / 2):            
            return '#FFFF00'  # Cor de alerta intermediária (amarela)
        
        return self.cor_inicial
    
    def validar_campos(self, card):
        """Valida se os campos relevantes estão preenchidos no cartão."""
        erros = []
        for campo, descricao in self.campos_obrigatorios.items():
            if not getattr(card, campo, None):
                erros.append(f"O campo '{campo}' ({descricao}) é obrigatório para esta coluna.")
        if erros:
            raise ValidationError(erros)
    
class ContatoInicialColumn(AbstractKanbanColumn):
    """Coluna para Contato Inicial."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='contato_inicial_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "lead_nome": "Nome do lead",
            "descricao": "Descrição inicial do lead",
        }


class VisitaImovelColumn(AbstractKanbanColumn):
    """Coluna para Visita ao Imóvel."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='visita_imovel_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "data_visita": "Data e hora da visita agendada",
            "observacoes_visita": "Observações sobre a visita",
        }


class NegociacaoColumn(AbstractKanbanColumn):
    """Coluna para Negociação."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='negociacao_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "valor_final": "Valor final da negociação",
            "tipo_garantia": "Tipo de garantia",
            "prazo_vigencia": "Prazo de vigência do contrato",
            "metodo_pagamento": "Método de pagamento",
        }


class DocumentacaoAnaliseCreditoColumn(AbstractKanbanColumn):
    """Coluna para Documentação e Análise de Crédito."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='documentacao_analise_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "documentos_anexados": "Documentos anexados para análise",
            "status_documentacao": "Status da documentação",
            "resultado_analise_credito": "Resultado da análise de crédito",
        }


class AssinaturaContratoColumn(AbstractKanbanColumn):
    """Coluna para Assinatura de Contrato."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='assinatura_contrato_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "data_assinatura": "Data da assinatura do contrato",
            "contrato_assinado": "Contrato assinado anexado",
        }


class ReprovadoColumn(AbstractKanbanColumn):
    """Coluna para Reprovado."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='reprovado_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "status_documentacao": "Status da documentação",
            "resultado_analise_credito": "Resultado da análise de crédito",
        }


class InativosColumn(AbstractKanbanColumn):
    """Coluna para Inativos."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='inativos_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "descricao": "Motivo da inatividade",
        }


class ContratosFirmadosColumn(AbstractKanbanColumn):
    """Coluna para Contratos Firmados."""
    kanban_cards = GenericRelation(KanbanCard, related_query_name='contratos_firmados_column')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.campos_obrigatorios = {
            "contrato_assinado": "Contrato assinado anexado",
            "data_assinatura": "Data da assinatura do contrato",
        }


class Kanban(models.Model):
    nome = models.CharField(max_length=100, help_text="Nome do Kanban")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição do Kanban")
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="kanban")

    def __str__(self):
        return f"Kanban: {self.nome} do Usuário: {self.usuario}"

   
    

class KanbanColumnOrder(models.Model):
    """Classe para gerenciar a ordem das colunas dentro de um Kanban."""
    kanban = models.ForeignKey(Kanban, on_delete=models.CASCADE, related_name="colunas")
    coluna_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    coluna_object_id = models.PositiveIntegerField()
    coluna = GenericForeignKey('coluna_content_type', 'coluna_object_id')
    posicao = models.PositiveIntegerField(help_text="Posição da coluna no Kanban")

    class Meta:
        unique_together = ('kanban', 'coluna_content_type', 'coluna_object_id')
        ordering = ['posicao']

    def __str__(self):
        return f"{self.kanban.nome} - {self.coluna.nome} (Posição {self.posicao})"
    

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para ajustar as posições de outras colunas, se necessário.
        """
        # Recupera todas as colunas do mesmo Kanban
        colunas = KanbanColumnOrder.objects.filter(kanban=self.kanban).exclude(id=self.id)

        # Valida se a posição é válida
        if self.posicao < 1:
            raise ValidationError("A posição deve ser maior ou igual a 1.")

        max_posicao = colunas.aggregate(Max('posicao'))['posicao__max'] or 0

        # Ajusta as posições das colunas apenas se necessário
        if colunas.filter(posicao=self.posicao).exists():
            colunas.filter(posicao__gte=self.posicao).update(posicao=F('posicao') + 1)

        # Garante que a posição não ultrapasse o máximo permitido
        if self.posicao > (max_posicao + 1):
            self.posicao = max_posicao + 1

        super().save(*args, **kwargs)

    def verificar_se_extende_abstract_column(self, coluna):
        """Verifica se a coluna fornecida é uma subclasse concreta de AbstractKanbanColumn."""
        model_class = coluna.__class__
        if not issubclass(model_class, AbstractKanbanColumn) or model_class._meta.abstract:
            raise ValidationError("A coluna associada deve ser uma subclasse concreta de AbstractKanbanColumn.")
        return True

    def associar_coluna(self, coluna, posicao):
        """
        Verifica e associa a coluna ao KanbanColumnOrder, salvando-a na posição especificada.
        """
        # Verifica se a coluna é uma subclasse de AbstractKanbanColumn
        if self.verificar_se_extende_abstract_column(coluna):
            # Define o tipo de conteúdo e ID do objeto
            self.coluna_content_type = ContentType.objects.get_for_model(coluna)
            self.coluna_object_id = coluna.id
            self.posicao = posicao
            self.save()
            
        return self
    

def criar_kanban_padrao(usuario):
    # Cria o Kanban associado ao usuário
    kanban = Kanban.objects.create(
        usuario=usuario,
        nome=f"Kanban de {usuario.username}",
        descricao="Kanban padrão do usuário"
    )

    # Define as colunas padrão com as posições corretas e cria as instâncias de cada coluna
    colunas_padrao = [
        (ContatoInicialColumn, "Contato Inicial", 1),
        (VisitaImovelColumn, "Visita ao Imóvel", 2),
        (NegociacaoColumn, "Negociação", 3),
        (DocumentacaoAnaliseCreditoColumn, "Documentação e Análise de Crédito", 4),
        (AssinaturaContratoColumn, "Assinatura do Contrato", 5),
        (ContratosFirmadosColumn, "Contratos Firmados", 6),
        (ReprovadoColumn, "Reprovado", 7),
        (InativosColumn, "Inativos", 8),
        
    ]

    # Itera sobre a lista de colunas padrão, criando cada uma e associando-a ao Kanban
    for coluna_class, nome, posicao in colunas_padrao:
        coluna = coluna_class.objects.create(nome=nome)
        KanbanColumnOrder.objects.create(kanban=kanban, coluna=coluna, posicao=posicao)



