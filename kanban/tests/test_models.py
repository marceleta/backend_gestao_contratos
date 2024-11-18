from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from usuario.models import Usuario
from kanban.models import (
    Kanban, KanbanCard, ContatoInicialColumn, VisitaImovelColumn,
    NegociacaoColumn, KanbanColumnOrder, criar_kanban_padrao
)
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from django.utils import timezone
from kanban.signals import criar_kanban_ao_criar_usuario


class KanbanModelTest(TestCase):

    def setUp(self):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        self.usuario = Usuario.objects.create(username="testuser")
        self.kanban = Kanban.objects.create(
            usuario=self.usuario,
            nome="Kanban Teste",
            descricao="Descrição do Kanban Teste"
        )

    def test_kanban_creation(self):
        self.assertEqual(self.kanban.nome, "Kanban Teste")
        self.assertEqual(self.kanban.usuario, self.usuario)

    def test_adicionar_coluna_em_posicao(self):
        coluna1 = ContatoInicialColumn.objects.create(nome="Contato Inicial")
        coluna2 = VisitaImovelColumn.objects.create(nome="Visita ao Imóvel")

        # Adiciona a coluna na posição específica e verifica ordenação
        self.kanban.adicionar_coluna_em_posicao(coluna1, posicao_desejada=1)
        self.kanban.adicionar_coluna_em_posicao(coluna2, posicao_desejada=2)

        colunas = self.kanban.colunas.order_by('posicao')
        self.assertEqual(colunas[0].coluna.nome, "Contato Inicial")
        self.assertEqual(colunas[1].coluna.nome, "Visita ao Imóvel")


    def test_validar_campos_obrigatorios_contato_inicial_column(self):
        coluna = ContatoInicialColumn.objects.create(nome="Contato Inicial")
        card_data_incompleto = {
            'descricao': "Descrição incompleta"
        }
        card_data_completo = {
            'lead_nome': "Lead Teste",
            'descricao': "Descrição completa"
        }

        # Criação de um KanbanCard sem os campos obrigatórios
        card_incompleto = KanbanCard(**card_data_incompleto)
        try:
            coluna.validar_campos(card_incompleto)
        except ValidationError as e:
            self.assertIn("O campo 'lead_nome' (Nome do lead) é obrigatório para esta coluna.", str(e))
        else:
            self.fail("Validar_campos não levantou exceção para dados incompletos.")

        # Criação de um KanbanCard com os campos obrigatórios
        card_completo = KanbanCard(**card_data_completo)
        try:
            coluna.validar_campos(card_completo)
        except ValidationError:
            self.fail("Validar_campos levantou uma exceção para dados completos.")


class KanbanCardModelTest(TestCase):

    def setUp(self):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        self.usuario = Usuario.objects.create(username="testuser")
        self.kanban = Kanban.objects.create(usuario=self.usuario)
        self.coluna = ContatoInicialColumn.objects.create(nome="Contato Inicial")

    def test_kanban_card_associar_a_coluna(self):
        card = KanbanCard.objects.create(
            lead_nome="Teste Lead",
            data_criacao=timezone.now(),
            content_type=ContentType.objects.get_for_model(ContatoInicialColumn),
            object_id=self.coluna.id
        )
        
        with self.assertRaises(ValidationError):
            card.associar_a_coluna(coluna="Invalida")  # Deve falhar para coluna inválida

        # Associação válida
        card.associar_a_coluna(self.coluna)
        self.assertEqual(card.content_object, self.coluna)

    def test_atualizar_cor(self):
        # Define data de criação que excede o prazo de alerta
        data_criacao = timezone.now() - timedelta(hours=5)
        card = KanbanCard.objects.create(
            lead_nome="Lead Teste",
            data_criacao=data_criacao,
            content_type=ContentType.objects.get_for_model(ContatoInicialColumn),
            object_id=self.coluna.id
        )

        # Define o prazo de alerta e salva a coluna
        self.coluna.prazo_alerta = 3  # 3 horas para disparar alerta vermelho
        self.coluna.save()

        # Associa coluna e atualiza cor
        card.associar_a_coluna(self.coluna)
        card.atualizar_cor()
        
        # Verifica se a cor do cartão é vermelha, indicando prazo excedido
        self.assertEqual(card.cor_atual, '#FF0000')  # Espera que a cor seja vermelha


class CriarKanbanPadraoTest(TestCase):

    def setUp(self):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        self.usuario = Usuario.objects.create(username="testuser")

    def test_criar_kanban_padrao(self):
        criar_kanban_padrao(self.usuario)
        kanban = Kanban.objects.get(usuario=self.usuario)
        self.assertEqual(kanban.colunas.count(), 8)
        # Verifica que a primeira coluna é "Contato Inicial"
        primeira_coluna = kanban.colunas.order_by('posicao').first().coluna
        self.assertEqual(primeira_coluna.nome, "Contato Inicial")
        

class KanbanColumnOrderModelTest(TestCase):

    def setUp(self):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        self.usuario = Usuario.objects.create(username="testuser")
        self.kanban = Kanban.objects.create(usuario=self.usuario)
        self.coluna = ContatoInicialColumn.objects.create(nome="Contato Inicial")

    def test_criar_kanban_column_order(self):
        column_order = KanbanColumnOrder.objects.create(
            kanban=self.kanban,
            coluna_content_type=ContentType.objects.get_for_model(ContatoInicialColumn),
            coluna_object_id=self.coluna.id,
            posicao=1
        )

        self.assertEqual(column_order.kanban, self.kanban)
        self.assertEqual(column_order.coluna, self.coluna)
        self.assertEqual(column_order.posicao, 1)

    def test_verificar_se_extende_abstract_column(self):
        column_order = KanbanColumnOrder(
            kanban=self.kanban,
            coluna_content_type=ContentType.objects.get_for_model(ContatoInicialColumn),
            coluna_object_id=self.coluna.id,
            posicao=1
        )

        # Validação bem-sucedida
        self.assertTrue(column_order.verificar_se_extende_abstract_column(self.coluna))

        # Validação falha para uma classe inválida
        with self.assertRaises(ValidationError):
            column_order.verificar_se_extende_abstract_column("Invalida")

    def test_associar_coluna(self):
        column_order = KanbanColumnOrder.objects.create(
            kanban=self.kanban,
            coluna_content_type=ContentType.objects.get_for_model(ContatoInicialColumn),
            coluna_object_id=self.coluna.id,
            posicao=1
        )

        nova_coluna = VisitaImovelColumn.objects.create(nome="Visita ao Imóvel")
        column_order.associar_coluna(nova_coluna, posicao=2)

        self.assertEqual(column_order.coluna, nova_coluna)
        self.assertEqual(column_order.posicao, 2)




