from django.test import TestCase
from core.models import PessoaFisica, Estado

class PessoaFisicaModelTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        self.pessoa_fisica = PessoaFisica.objects.create(
            nome="João da Silva",
            email="joao@example.com",
            telefone="12345-6789",
            endereco="Rua A",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="12345-678",
            cpf="123.456.789-00",
            identidade="MG-12.345.678",
            orgao_expeditor="SSP-MG",
            data_nascimento="1980-01-01",
            estado_civil="Solteiro(a)",
            nacionalidade="Brasileiro"
        )

    def test_create_pessoa_fisica(self):
        self.assertEqual(self.pessoa_fisica.nome, "João da Silva")

    def test_read_pessoa_fisica(self):
        pessoa_fisica_lida = PessoaFisica.objects.get(cpf="123.456.789-00")
        self.assertEqual(pessoa_fisica_lida.nome, "João da Silva")

    def test_update_pessoa_fisica(self):
        self.pessoa_fisica.nome = "João Silva"
        self.pessoa_fisica.save()
        pessoa_fisica_atualizada = PessoaFisica.objects.get(cpf="123.456.789-00")
        self.assertEqual(pessoa_fisica_atualizada.nome, "João Silva")

    def test_delete_pessoa_fisica(self):
        self.pessoa_fisica.delete()
        self.assertFalse(PessoaFisica.objects.filter(cpf="123.456.789-00").exists())

