from django.test import TestCase
from core.models import Estado
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from proprietario.models import Proprietario, Representante
from locatario.models import Locatario
from procuracao.models import Procuracao
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_test_pdf():
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, "Este é um PDF de teste.")
    p.showPage()
    p.save()

    buffer.seek(0)
    
    return SimpleUploadedFile("procuracao.pdf", buffer.read(), content_type="application/pdf")


class ProcuracaoModelTest(TestCase):

    def setUp(self):
        #Cria um estado para ser utilizando nos testes
        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')

        #Cria um proprietario para ser o ortogante da procuração
        self.outorgante = Proprietario.objects.create(
            nome="José Silva",
            cpf="12345678901",
            email="jose.silva@example.com",
            endereco="Rua A, 123",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="01000-000",
            nacionalidade="Brasileiro",
            estado_civil="Casado(a)",
            data_nascimento="1970-01-01"
        )

         # Criando um representante para ser o representante da procuração
        self.representante = Representante.objects.create(
            nome="Maria Souza",
            cpf="10987654321",
            email="maria.souza@example.com",
            endereco="Rua B, 456",
            bairro="Jardins",
            cidade="São Paulo",
            estado=self.estado,
            cep="02000-000",
            nacionalidade="Brasileira",
            estado_civil="Solteiro(a)",
            data_nascimento="1980-01-01"
        )

        self.documento_simulado = create_test_pdf()

        # Criando uma procuração
        self.procuracao = Procuracao.objects.create(
            outorgante=self.outorgante,
            representante=self.representante,
            data_inicio="2024-01-01",
            data_validade="2024-12-31",
            escopo="Representação em negociações de imóveis.",
            documento=self.documento_simulado
        )

    def test_procuracao_creation(self):
        self.assertEqual(self.procuracao.outorgante.nome, "José Silva")
        self.assertEqual(self.procuracao.representante.nome, "Maria Souza")
        self.assertEqual(self.procuracao.escopo, "Representação em negociações de imóveis.")
        self.assertEqual(self.procuracao.data_validade, "2024-12-31")


class ProcuracaoAPITestCase(APITestCase):

    def setUp(self):
        # Configuração inicial dos dados
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.estado = Estado.objects.create(sigla='SP', nome='São Paulo')
        
        # Criação do proprietário e representante
        self.outorgante = Proprietario.objects.create(
            nome="José Silva",
            cpf="12345678901",
            email="jose.silva@example.com",
            endereco="Rua A, 123",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="01000-000",
            nacionalidade="Brasileiro",
            estado_civil="Casado(a)",
            data_nascimento="1970-01-01"
        )
        self.representante = Representante.objects.create(
            nome="Maria Souza",
            cpf="10987654321",
            email="maria.souza@example.com",
            endereco="Rua B, 456",
            bairro="Jardins",
            cidade="São Paulo",
            estado=self.estado,
            cep="02000-000",
            nacionalidade="Brasileira",
            estado_civil="Solteiro(a)",
            data_nascimento="1980-01-01"
        )

        self.documento_simulado = create_test_pdf()
        self.documento_simulado.seek(0)
        # Criação da procuração para testes
        self.procuracao = Procuracao.objects.create(
            outorgante=self.outorgante,
            representante=self.representante,
            data_inicio="2024-01-01",
            data_validade="2024-12-31",
            escopo="Representação em negociações de imóveis.",
            documento=self.documento_simulado
        )

    def test_create_procuracao(self):
        url = reverse('procuracao-list')
        documento_simulado = create_test_pdf()
        documento_simulado.seek(0)
        data = {
            "outorgante": self.outorgante.id,
            "representante": self.representante.id,
            "data_inicio": "2024-01-01",
            "data_validade": "2024-12-31",
            "escopo": "Representação em negociações de imóveis.",
            "documento": documento_simulado
        }
        #print(f"Tamanho do arquivo: {len(documento_simulado.read())}")
        documento_simulado.seek(0)
        response = self.client.post(url, data, format='multipart')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Procuracao.objects.count(), 2)  # Já existe uma procuração criada no setUp

    def test_get_procuracao(self):
        url = reverse('procuracao-detail', args=[self.procuracao.id])
        response = self.client.get(url, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['escopo'], self.procuracao.escopo)

    def test_update_procuracao(self):
        documento_simulado = create_test_pdf()
        documento_simulado.seek(0)
        data = {
            "outorgante": self.outorgante.id,
            "representante": self.representante.id,
            "data_inicio": "2024-01-01",
            "data_validade": "2025-12-31",  # Atualizando a data de validade
            "escopo": "Representação em vendas de imóveis.",
            "documento":documento_simulado
        }
        url = reverse('procuracao-detail', args=[self.procuracao.id])
        response = self.client.put(url, data, format='multipart')
        #print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Procuracao.objects.get(id=self.procuracao.id).data_validade.strftime("%Y-%m-%d"), "2025-12-31")
        self.assertEqual(Procuracao.objects.get(id=self.procuracao.id).escopo, "Representação em vendas de imóveis.")