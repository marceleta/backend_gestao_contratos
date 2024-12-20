from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from usuario.models import Usuario
from django.utils import timezone
from kanban.models import (
    Kanban, KanbanCard, KanbanColumnOrder, KanbanColumn, criar_kanban_padrao
)
from kanban.signals import criar_kanban_ao_criar_usuario


class KanbanModelTest(TestCase):

    def setUp(self):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Criação de um usuário e Kanban associado
        self.usuario = Usuario.objects.create(username="testuser")
        self.kanban = Kanban.objects.create(
            usuario=self.usuario,
            nome="Kanban Teste",
            descricao="Descrição do Kanban Teste"
        )

    def test_kanban_creation(self):
        # Testa a criação do Kanban e seus atributos
        self.assertEqual(self.kanban.nome, "Kanban Teste")
        self.assertEqual(self.kanban.usuario, self.usuario)

    def test_adicionar_coluna_em_posicao(self):
        # Cria colunas
        coluna1 = KanbanColumn.objects.create(nome="Contato Inicial")
        coluna2 = KanbanColumn.objects.create(nome="Visita ao Imóvel")

        # Adiciona as colunas em posições específicas e verifica a ordem
        KanbanColumnOrder.objects.create(kanban=self.kanban, coluna=coluna1, posicao=1)
        KanbanColumnOrder.objects.create(kanban=self.kanban, coluna=coluna2, posicao=2)

        colunas = KanbanColumnOrder.objects.filter(kanban=self.kanban).order_by('posicao')
        self.assertEqual(colunas[0].coluna.nome, "Contato Inicial")
        self.assertEqual(colunas[1].coluna.nome, "Visita ao Imóvel")

    def test_validar_campos_obrigatorios_coluna(self):
        # Cria uma coluna com campos obrigatórios
        campos_obrigatorios = {
            "lead_nome": "Nome do lead",
            "descricao": "Descrição inicial do lead"
        }
        coluna = KanbanColumn.objects.create(nome="Contato Inicial", meta_dados={"campos_obrigatorios": campos_obrigatorios})

        # Testa card incompleto
        card_incompleto = KanbanCard(
            descricao="Descrição incompleta",
            coluna=coluna
        )
        try:
            coluna.validar_campos(card_incompleto)
        except ValidationError as e:
            self.assertIn("O campo 'lead_nome' (Nome do lead) é obrigatório para esta coluna.", str(e))
        else:
            self.fail("Validar_campos não levantou exceção para dados incompletos.")

        # Testa card completo
        card_completo = KanbanCard(
            lead_nome="Lead Teste",
            descricao="Descrição completa",
            coluna=coluna
        )
        try:
            coluna.validar_campos(card_completo)
        except ValidationError:
            self.fail("Validar_campos levantou uma exceção para dados completos.")

    def test_associar_card_a_coluna(self):
        # Cria uma coluna
        coluna = KanbanColumn.objects.create(nome="Contato Inicial")

        # Cria um card e associa à coluna
        card = KanbanCard.objects.create(
            lead_nome="Lead Teste",
            descricao="Descrição do lead",
            coluna=coluna
        )

        self.assertEqual(card.coluna, coluna)
        self.assertEqual(card.lead_nome, "Lead Teste")
        self.assertEqual(card.descricao, "Descrição do lead")

    def test_atualizar_cor_do_card(self):
        # Cria uma coluna e um card associado
        coluna = KanbanColumn.objects.create(nome="Contato Inicial", prazo_alerta=2)
        card = KanbanCard.objects.create(
            lead_nome="Lead Teste",
            descricao="Descrição do lead",
            coluna=coluna
        )

        # Simula a atualização da cor do card com base no prazo
        card.data_criacao = timezone.now() - timezone.timedelta(hours=3)
        card.atualizar_cor()
        self.assertEqual(card.cor_atual, coluna.cor_alerta)

        card.data_criacao = timezone.now() - timezone.timedelta(hours=1)
        card.atualizar_cor()
        self.assertEqual(card.cor_atual, "#FFFF00")  # Alerta intermediário

        card.data_criacao = timezone.now()
        card.atualizar_cor()
        self.assertEqual(card.cor_atual, coluna.cor_inicial)


class KanbanCardModelTest(TestCase):

    def setUp(self):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Criação de usuário e Kanban
        self.usuario = Usuario.objects.create(username="testuser")
        self.kanban = Kanban.objects.create(
            usuario=self.usuario,
            nome="Kanban Teste",
            descricao="Descrição do Kanban Teste"
        )
        # Criação de uma coluna no Kanban
        self.coluna = KanbanColumn.objects.create(
            nome="Contato Inicial",
            meta_dados={"campos_obrigatorios": {"lead_nome": "Nome do lead"}}
        )

    def test_kanban_card_associar_a_coluna(self):
        # Criação de um card
        card = KanbanCard.objects.create(
            lead_nome="Teste Lead",
            descricao="Descrição do lead",
            coluna=self.coluna
        )

        # Tentativa de associação com uma coluna inválida
        with self.assertRaises(ValidationError):
            card.validar_e_associar_coluna(coluna="Invalida")  # Deve falhar para coluna inválida

        # Associação válida
        card.validar_e_associar_coluna(self.coluna)
        self.assertEqual(card.coluna, self.coluna)

    def test_validar_campos_obrigatorios(self):
        # Criação de um card sem campos obrigatórios
        card_invalido = KanbanCard.objects.create(
            descricao="Descrição incompleta",
            coluna=self.coluna
        )

        with self.assertRaises(ValidationError):
            self.coluna.validar_campos(card_invalido)  # Deve falhar devido à falta de campos obrigatórios

        # Criação de um card com campos obrigatórios
        card_valido = KanbanCard.objects.create(
            lead_nome="Lead Teste",
            descricao="Descrição completa",
            coluna=self.coluna
        )

        try:
            self.coluna.validar_campos(card_valido)  # Não deve levantar exceção
        except ValidationError:
            self.fail("Erro ao validar campos obrigatórios para um card válido.")




class CriarKanbanPadraoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Cria um usuário apenas uma vez para todos os testes
        cls.usuario = Usuario.objects.create(username="testuser")

    def test_criar_kanban_padrao(self):
        """
        Testa se o Kanban padrão é criado corretamente para um usuário,
        com 8 colunas e na ordem definida.
        """
        # Cria o Kanban padrão
        kanban = criar_kanban_padrao(self.usuario)

        # Verifica se o Kanban foi criado e está associado ao usuário correto
        self.assertEqual(kanban.usuario, self.usuario)
        self.assertEqual(kanban.colunas.count(), 8)

        # Obtém as colunas criadas e verifica a ordem e os nomes
        colunas_esperadas = [
            "Contato Inicial",
            "Visita ao Imóvel",
            "Negociação",
            "Documentação e Análise de Crédito",
            "Assinatura do Contrato",
            "Contratos Firmados",
            "Reprovado",
            "Inativos"
        ]

        colunas_criadas = (
            KanbanColumnOrder.objects.filter(kanban=kanban)
            .order_by("posicao")
            .values_list("coluna__nome", flat=True)
        )

        self.assertEqual(list(colunas_criadas), colunas_esperadas)

    def test_meta_dados_das_colunas(self):
        """
        Testa se as colunas padrão têm os meta_dados corretos.
        """
        # Cria o Kanban padrão
        kanban = criar_kanban_padrao(self.usuario)

        # Define os meta_dados esperados
        meta_dados_esperados = {
            "Contato Inicial": {
                "lead_nome": "Nome do lead",
                "descricao": "Descrição inicial do lead",
            },
            "Visita ao Imóvel": {
                "data_visita": "Data e hora da visita agendada",
                "observacoes_visita": "Observações sobre a visita",
            },
            "Negociação": {
                "valor_final": "Valor final da negociação",
                "tipo_garantia": "Tipo de garantia",
                "prazo_vigencia": "Prazo de vigência do contrato",
                "metodo_pagamento": "Método de pagamento",
            },
            "Documentação e Análise de Crédito": {
                "documentos_anexados": "Documentos anexados para análise",
                "status_documentacao": "Status da documentação",
                "resultado_analise_credito": "Resultado da análise de crédito",
            },
            "Assinatura do Contrato": {
                "data_assinatura": "Data da assinatura do contrato",
                "contrato_assinado": "Contrato assinado anexado",
            },
            "Contratos Firmados": {
                "contrato_assinado": "Contrato assinado anexado",
                "data_assinatura": "Data da assinatura do contrato",
            },
            "Reprovado": {
                "status_documentacao": "Status da documentação",
                "resultado_analise_credito": "Resultado da análise de crédito",
            },
            "Inativos": {
                "descricao": "Motivo da inatividade",
            },
        }

        # Verifica os meta_dados de cada coluna
        for coluna_order in kanban.colunas.all():
            nome_coluna = coluna_order.coluna.nome
            self.assertIn(nome_coluna, meta_dados_esperados)
            self.assertEqual(coluna_order.coluna.meta_dados, meta_dados_esperados[nome_coluna])

        

class KanbanColumnOrderModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        post_save.disconnect(criar_kanban_ao_criar_usuario, sender=Usuario)
        # Criação inicial de usuário, kanban e colunas
        cls.usuario = Usuario.objects.create(username="testuser")
        cls.kanban = Kanban.objects.create(usuario=cls.usuario)
        cls.coluna1 = KanbanColumn.objects.create(nome="Contato Inicial")
        cls.coluna2 = KanbanColumn.objects.create(nome="Visita ao Imóvel")
        cls.coluna3 = KanbanColumn.objects.create(nome="Negociação")


    def setUp(self):
        # Cada teste deve ter colunas ordenadas para garantir a consistência dos dados
        KanbanColumnOrder.objects.create(kanban=self.kanban, coluna=self.coluna1, posicao=1)
        KanbanColumnOrder.objects.create(kanban=self.kanban, coluna=self.coluna2, posicao=2)
        KanbanColumnOrder.objects.create(kanban=self.kanban, coluna=self.coluna3, posicao=3)


    def test_criar_kanban_column_order(self):
        """
        Testa a criação de uma `KanbanColumnOrder` associada a um Kanban.
        """
        # Criação inicial da ordem de colunas (verifica se já existe para evitar duplicação)
        column_order, created = KanbanColumnOrder.objects.get_or_create(
            kanban=self.kanban,
            coluna=self.coluna1,
            defaults={'posicao': 1}
        )
        #print(f'created: {created}')

        # Verifica se a instância foi criada
        self.assertFalse(created, "A coluna já existia e não foi criada novamente.")

        # Verifica os valores dos atributos
        self.assertEqual(column_order.kanban, self.kanban)
        self.assertEqual(column_order.coluna, self.coluna1)
        self.assertEqual(column_order.posicao, 1)


    def test_posicao_ajustada_automaticamente(self):
        """
        Testa se as posições das colunas são ajustadas automaticamente ao inserir
        uma nova coluna na mesma posição.
        """
        # Inicialmente temos 3 colunas criadas com as posições 1, 2 e 3
        # Vamos adicionar uma nova coluna, `coluna4`, na posição 1
        nova_coluna = KanbanColumn.objects.create(nome="Nova Coluna Ajustada")

        # Utilizando o método `adicionar_e_reordenar` para associar a nova coluna na posição 1
        KanbanColumnOrder.adicionar_e_reordenar(kanban=self.kanban, coluna=nova_coluna, posicao=1)

        # Recupera as colunas ordenadas por posição para verificação
        colunas = KanbanColumnOrder.objects.filter(kanban=self.kanban).order_by("posicao")

        # Verifica se a nova coluna foi adicionada corretamente
        self.assertEqual(colunas[0].coluna, nova_coluna)  # Nova coluna deve ocupar a posição 1
        self.assertEqual(colunas[1].coluna, self.coluna1)  # Coluna original deve ser movida para posição 2
        self.assertEqual(colunas[2].coluna, self.coluna2)  # Coluna original deve ser movida para posição 3
        self.assertEqual(colunas[3].coluna, self.coluna3)  # Coluna original deve ser movida para posição 4



    def test_adicionar_e_reordenar(self):
        """
        Testa o método estático `associar_coluna` para criar e associar uma nova coluna
        ao Kanban e ajustar sua posição.
        """

        # Criação de uma nova coluna
        nova_coluna = KanbanColumn.objects.create(nome="Documentação e Análise de Crédito")

        # Utilizando o método estático para associar a nova coluna na posição 2
        KanbanColumnOrder.adicionar_e_reordenar(kanban=self.kanban, coluna=nova_coluna, posicao=2)

        # Recupera as colunas ordenadas por posição para verificação
        colunas = KanbanColumnOrder.objects.filter(kanban=self.kanban).order_by("posicao")

        # Verifica se a nova coluna foi adicionada corretamente
        self.assertEqual(colunas[1].coluna, nova_coluna)  # A nova coluna deve estar na posição 2
        self.assertEqual(colunas[0].coluna, self.coluna1)  # A coluna original permanece na posição 1


    def test_ordem_das_colunas_kanban(self):
        """
        Testa se as colunas de um Kanban estão sendo ordenadas corretamente.
        """
        # Criação de uma nova coluna e associação ao kanban
        coluna4 = KanbanColumn.objects.create(nome="Nova Coluna")
        
        # Utilizando o método `adicionar_e_reordenar` para adicionar a coluna4 na posição 2
        KanbanColumnOrder.adicionar_e_reordenar(kanban=self.kanban, coluna=coluna4, posicao=2)

        # Recupera as colunas ordenadas por posição para verificação
        colunas_ordenadas = KanbanColumnOrder.objects.filter(kanban=self.kanban).order_by("posicao")

        # Verifica se as colunas estão ordenadas corretamente
        self.assertEqual(colunas_ordenadas[0].coluna, self.coluna1)  # A coluna original 1 deve permanecer na posição 1
        self.assertEqual(colunas_ordenadas[1].coluna, coluna4)       # Nova coluna deve ocupar a posição 2
        self.assertEqual(colunas_ordenadas[2].coluna, self.coluna2)  # Coluna2 deve mover para a posição 3
        self.assertEqual(colunas_ordenadas[3].coluna, self.coluna3)  # Coluna3 deve mover para a posição 4


    
    def test_remover_coluna_com_cards(self):
        """
        Testa a tentativa de remover uma coluna que possui cards.
        Deve levantar um ValidationError.
        """
        # Criação de um card associado à coluna2
        KanbanCard.objects.create(lead_nome="Lead Teste", descricao="Descrição do lead", coluna=self.coluna2)

        # Tentativa de remover a coluna com cards deve resultar em um ValidationError
        with self.assertRaises(ValidationError) as context:
            KanbanColumnOrder.remover_coluna(kanban=self.kanban, coluna=self.coluna2)

        # Extrair a mensagem do ValidationError para comparação
        mensagens_de_erro = context.exception.messages
        self.assertIn(
            "Existem cards associados a esta coluna. Remova ou mova os cards antes de excluir a coluna.",
            mensagens_de_erro
        )

        # Verifica se a coluna e os cards ainda existem
        self.assertTrue(KanbanColumn.objects.filter(pk=self.coluna2.pk).exists())
        self.assertTrue(KanbanCard.objects.filter(coluna=self.coluna2).exists())


    def test_remover_coluna_sem_cards(self):
        """
        Testa a remoção de uma coluna que não possui cards.
        """
        # Obtém a quantidade inicial de colunas e ordens de colunas
        coluna_order_count = KanbanColumnOrder.objects.filter(kanban=self.kanban).count()
        coluna_count = KanbanColumn.objects.count()

        # Remove a coluna que não possui cards
        KanbanColumnOrder.remover_coluna(kanban=self.kanban, coluna=self.coluna2)

        # Verifica se a quantidade de KanbanColumnOrder diminuiu em 1
        self.assertEqual(
            KanbanColumnOrder.objects.filter(kanban=self.kanban).count(),
            coluna_order_count - 1
        )

        # Verifica se a quantidade de KanbanColumn diminuiu em 1
        self.assertEqual(
            KanbanColumn.objects.count(),
            coluna_count - 1
        )



    def tearDown(self):
        # Limpa as alterações realizadas em cada teste para que não interfiram nos demais testes
        KanbanColumnOrder.objects.filter(kanban=self.kanban).delete()
        KanbanCard.objects.all().delete()





