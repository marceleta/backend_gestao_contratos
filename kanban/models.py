from usuario.models import Usuario
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from django.db.models import F, Max
from imovel.models import Imovel




class KanbanColumn(models.Model):
    nome = models.CharField(max_length=100)
    meta_dados = models.JSONField(default=dict, blank=True)
    prazo_alerta = models.PositiveIntegerField(default=3)  # Prazo em horas
    cor_inicial = models.CharField(max_length=7, default="#00FF00")
    cor_alerta = models.CharField(max_length=7, default="#FF0000")

    def validar_campos(self, card):
        """Valida se os campos obrigatórios da coluna estão preenchidos no cartão."""
        erros = []
        for campo, descricao in self.meta_dados.get("campos_obrigatorios", {}).items():
            if not getattr(card, campo, None):
                erros.append(f"O campo '{campo}' ({descricao}) é obrigatório para esta coluna.")
        if erros:
            raise ValidationError(erros)

    def verificar_prazo(self, data_criacao):

        alerta_cor = self.cor_inicial
        alerta_prazo = float(self.prazo_alerta)

        #print(f'prazo_alerta: {alerta_prazo}')
        #print(f'data_criacao: {data_criacao}')
        #print(f'timezone.now(): {timezone.now()}')
        """Calcula a cor baseada no prazo de alerta."""
        horas_passadas = (timezone.now() - data_criacao).total_seconds() / 3600
        #print(f'horas passadas: {horas_passadas}')
        
        if horas_passadas > alerta_prazo:            
            alerta_cor = self.cor_alerta
        elif horas_passadas >= (alerta_prazo / 2):            
           alerta_cor = '#FFFF00'  # Cor de alerta intermediária (amarela)
        
        return alerta_cor

    def __str__(self):
        return f"Coluna: {self.nome}"
    

class KanbanCard(models.Model):
    lead_nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)  # Define automaticamente a data de criação
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    data_prazo = models.DateTimeField(null=True, blank=True)
    cor_atual = models.CharField(max_length=7, default='#00FF00')  # Cor inicial (verde)
    dados_adicionais = models.JSONField(default=dict, blank=True, help_text="Campo para dados dinâmicos adicionais")
    contato = models.JSONField(
        default=dict,
        blank=True,
        help_text="Informações de contato do lead, como telefone, WhatsApp, e e-mail",
        null=True,
    )

    # Campos específicos para cada coluna
    data_visita = models.DateTimeField(null=True, blank=True, help_text="Data e hora da visita agendada")
    observacoes_visita = models.TextField(blank=True, help_text="Observações sobre a visita")
    valor_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor final da negociação")
    tipo_garantia = models.CharField(max_length=100, blank=True, help_text="Tipo de garantia")
    prazo_vigencia = models.CharField(max_length=100, blank=True, help_text="Prazo de vigência do contrato")
    metodo_pagamento = models.CharField(max_length=100, blank=True, help_text="Método de pagamento")
    documentos_anexados = models.TextField(blank=True, help_text="Documentos anexados para análise")
    status_documentacao = models.CharField(max_length=100, blank=True, help_text="Status da documentação")
    resultado_analise_credito = models.CharField(max_length=100, blank=True, help_text="Resultado da análise de crédito")
    data_assinatura = models.DateTimeField(null=True, blank=True, help_text="Data da assinatura do contrato")
    contrato_assinado = models.TextField(blank=True, help_text="Contrato assinado anexado")


    # Campos necessários para associar a uma coluna do Kanban
    coluna = models.ForeignKey(
        KanbanColumn,
        on_delete=models.CASCADE,
        related_name="cards",
        help_text="Coluna do Kanban à qual este card está associado"
    )

    imovel = models.ForeignKey(
        Imovel,
        on_delete=models.CASCADE,
        related_name='imovel',
        help_text="Imovel que o contato está interessado",
        null=True,
        blank=True
    )

    def validar_e_associar_coluna(self, coluna):
        """
        Valida e associa o cartão a uma coluna do Kanban.
        """
        if not isinstance(coluna, KanbanColumn):
            raise ValidationError("A coluna deve ser uma instância de KanbanColumn.")
        
        # Valida os campos obrigatórios da coluna
        coluna.validar_campos(self)
        
        # Associa a coluna e salva o card
        self.coluna = coluna
        self.save()

    def atualizar_cor(self):
        """
        Atualiza a cor do cartão com base no prazo definido pela coluna.
        """
        if self.data_criacao:
            self.cor_atual = self.coluna.verificar_prazo(self.data_criacao)
            self.save()

    def __str__(self):
        return f"Lead: {self.lead_nome} na Coluna: {self.coluna.nome}"



class Kanban(models.Model):
    nome = models.CharField(max_length=100, help_text="Nome do Kanban")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição do Kanban")
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="kanban")

    def __str__(self):
        return f"Kanban: {self.nome} do Usuário: {self.usuario}"
    

class KanbanColumnOrder(models.Model):
    kanban = models.ForeignKey(Kanban, on_delete=models.CASCADE, related_name="colunas")
    coluna = models.ForeignKey(KanbanColumn, on_delete=models.CASCADE, related_name="ordem")
    posicao = models.PositiveIntegerField()

    class Meta:
        ordering = ['posicao']
        unique_together = ('kanban', 'coluna')
        

    @staticmethod
    def adicionar_e_reordenar(kanban, coluna, posicao):
        """
        Associa uma nova coluna ao Kanban ou ajusta a posição de uma coluna existente.
        """
        if not isinstance(coluna, KanbanColumn):
            raise ValidationError("A coluna fornecida deve ser uma instância de KanbanColumn.")

        if posicao < 1:
            raise ValidationError("A posição deve ser maior ou igual a 1.")
        

        colunas_existentes = KanbanColumnOrder.objects.filter(kanban=kanban)
        max_posicao = colunas_existentes.aggregate(Max('posicao'))['posicao__max'] or 0

        if posicao > max_posicao + 1:
            posicao = max_posicao + 1

        # Ajusta as posições das colunas, se necessário
        if colunas_existentes.filter(posicao=posicao).exists():
            colunas_existentes.filter(posicao__gte=posicao).update(posicao=F('posicao') + 1)


        # Cria ou atualiza o KanbanColumnOrder
        column_order, created = KanbanColumnOrder.objects.update_or_create(
            kanban=kanban,
            coluna=coluna,
            defaults={'posicao': posicao}
        )
        return column_order
    
    @staticmethod
    def remover_coluna(kanban, coluna):
        #import pdb
        #pdb.set_trace()

        """
        Remove uma coluna específica do Kanban e ajusta as posições das colunas restantes.
        """
        try:
            # Obter a instância de KanbanColumnOrder para a coluna
            coluna_order = KanbanColumnOrder.objects.get(kanban=kanban, coluna=coluna)
        except KanbanColumnOrder.DoesNotExist:
            raise ValidationError("A coluna especificada não está associada a este Kanban.")

        # Verificar se a coluna possui cards
        if KanbanCard.objects.filter(coluna=coluna).exists():
            raise ValidationError("Existem cards associados a esta coluna. Remova ou mova os cards antes de excluir a coluna.")

        # Deletar a coluna e a ordem
        coluna_order.delete()
        coluna.delete()

        # Reordenar as colunas restantes
        colunas_restantes = KanbanColumnOrder.objects.filter(kanban=kanban).order_by('posicao')
        for index, coluna_order in enumerate(colunas_restantes):
            coluna_order.posicao = index + 1  # Reatribuir posição de forma sequencial
        
        # Salvar em um único comando para melhorar desempenho
        KanbanColumnOrder.objects.bulk_update(colunas_restantes, ['posicao'])

        return True


    

def criar_kanban_padrao(usuario):
    # Cria o Kanban associado ao usuário
    kanban = Kanban.objects.create(
        usuario=usuario,
        nome=f"Kanban de {usuario.username}",
        descricao="Kanban padrão do usuário"
    )

    # Define as colunas padrão com suas posições e campos obrigatórios
    colunas_padrao = [
        ("Contato Inicial", 1, {
            "lead_nome": "Nome do lead",
            "descricao": "Descrição inicial do lead",
        }),
        ("Visita ao Imóvel", 2, {
            "data_visita": "Data e hora da visita agendada",
            "observacoes_visita": "Observações sobre a visita",
        }),
        ("Negociação", 3, {
            "valor_final": "Valor final da negociação",
            "tipo_garantia": "Tipo de garantia",
            "prazo_vigencia": "Prazo de vigência do contrato",
            "metodo_pagamento": "Método de pagamento",
        }),
        ("Documentação e Análise de Crédito", 4, {
            "documentos_anexados": "Documentos anexados para análise",
            "status_documentacao": "Status da documentação",
            "resultado_analise_credito": "Resultado da análise de crédito",
        }),
        ("Assinatura do Contrato", 5, {
            "data_assinatura": "Data da assinatura do contrato",
            "contrato_assinado": "Contrato assinado anexado",
        }),
        ("Contratos Firmados", 6, {
            "contrato_assinado": "Contrato assinado anexado",
            "data_assinatura": "Data da assinatura do contrato",
        }),
        ("Reprovado", 7, {
            "status_documentacao": "Status da documentação",
            "resultado_analise_credito": "Resultado da análise de crédito",
        }),
        ("Inativos", 8, {
            "descricao": "Motivo da inatividade",
        }),
    ]

    # Itera sobre a lista de colunas padrão, criando cada uma e associando-a ao Kanban
    for nome, posicao, campos_obrigatorios in colunas_padrao:
        # Cria a coluna específica
        coluna = KanbanColumn.objects.create(nome=nome, meta_dados=campos_obrigatorios)        
        coluna.save()
        # Associa a coluna ao Kanban com a ordem definida
        KanbanColumnOrder.objects.create(
            kanban=kanban,
            coluna=coluna,
            posicao=posicao
        )

    return kanban




