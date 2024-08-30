from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from core.models import Telefone, PessoaFisica, Estado

class TelefoneModelTest(TestCase):

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
            data_nascimento="1980-01-01",  # Adicionando data_nascimento
            estado_civil="Solteiro(a)",
            nacionalidade="Brasileiro"
        )
        self.telefone = Telefone.objects.create(
            numero="(11) 99999-9999",
            tipo="Celular",
            content_type=ContentType.objects.get_for_model(PessoaFisica),
            object_id=self.pessoa_fisica.id
        )

    def test_create_telefone(self):
        self.assertEqual(self.telefone.numero, "(11) 99999-9999")
        self.assertEqual(self.telefone.tipo, "Celular")

    def test_read_telefone(self):
        telefone_lido = Telefone.objects.get(numero="(11) 99999-9999")
        self.assertEqual(telefone_lido.tipo, "Celular")

    def test_update_telefone(self):
        self.telefone.tipo = "Comercial"
        self.telefone.save()
        telefone_atualizado = Telefone.objects.get(numero="(11) 99999-9999")
        self.assertEqual(telefone_atualizado.tipo, "Comercial")

    def test_delete_telefone(self):
        self.telefone.delete()
        self.assertFalse(Telefone.objects.filter(numero="(11) 99999-9999").exists())
