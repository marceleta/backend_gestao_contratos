from django.test import TestCase
from pipeline.models import Lead
from usuario.models import Usuario
from django.utils import timezone
from rest_framework.test import APIClient
from unittest.mock import MagicMock

class LeadCRUDTests(TestCase):

    def setUp(self):

        self.client = APIClient()
        self.user = Usuario.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

        self.imovel = MagicMock()
        self.imovel.nome = 'Imóvel Teste'
        
        self.consultor = Usuario.objects.create(username="consultor_test")

    def test_create_lead(self):
        lead = Lead.objects.create(
            nome="Lead Teste",
            contato="123456789",
            email="lead@teste.com",
            etapa_kanban=Lead.ETAPA_NOVO,
            imovel_interesse=self.imovel,
            consultor=self.consultor
        )
        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(lead.nome, "Lead Teste")
        self.assertEqual(lead.etapa_kanban, Lead.ETAPA_NOVO)

    def test_read_lead(self):
        lead = Lead.objects.create(
            nome="Lead Teste",
            contato="123456789",
            email="lead@teste.com",
            etapa_kanban=Lead.ETAPA_NOVO,
            imovel_interesse=self.imovel,
            consultor=self.consultor
        )
        retrieved_lead = Lead.objects.get(id=lead.id)
        self.assertEqual(retrieved_lead.nome, "Lead Teste")
        self.assertEqual(retrieved_lead.contato, "123456789")

    def test_update_lead(self):
        lead = Lead.objects.create(
            nome="Lead Teste",
            contato="123456789",
            email="lead@teste.com",
            etapa_kanban=Lead.ETAPA_NOVO,
            imovel_interesse=self.imovel,
            consultor=self.consultor
        )
        lead.nome = "Lead Atualizado"
        lead.save()
        updated_lead = Lead.objects.get(id=lead.id)
        self.assertEqual(updated_lead.nome, "Lead Atualizado")

    def test_delete_lead(self):
        lead = Lead.objects.create(
            nome="Lead Teste",
            contato="123456789",
            email="lead@teste.com",
            etapa_kanban=Lead.ETAPA_NOVO,
            imovel_interesse=self.imovel,
            consultor=self.consultor
        )
        lead.delete()
        self.assertEqual(Lead.objects.count(), 0)
