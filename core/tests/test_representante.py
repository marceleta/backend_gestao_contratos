from django.test import TestCase
from core.models import PessoaFisica, PessoaJuridica, Representante, Estado

class RepresentanteModelTest(TestCase):

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
        self.pessoa_juridica = PessoaJuridica.objects.create(
            nome="Empresa X",
            email="contato@empresax.com",
            telefone="12345-6789",
            endereco="Av. Principal, 1000",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="12345-678",
            cnpj="12.345.678/0001-99",
            data_fundacao="2000-01-01"
        )
        self.representante = Representante.objects.create(
            pessoa_fisica=self.pessoa_fisica,
            pessoa_juridica=self.pessoa_juridica,
            cargo="Diretor",
            nivel_autoridade="Diretor"
        )

    def test_create_representante(self):
        self.assertEqual(self.representante.cargo, "Diretor")

    def test_read_representante(self):
        representante_lido = Representante.objects.get(
            pessoa_fisica=self.pessoa_fisica, pessoa_juridica=self.pessoa_juridica
        )
        self.assertEqual(representante_lido.cargo, "Diretor")

    def test_update_representante(self):
        self.representante.cargo = "Gerente"
        self.representante.save()
        representante_atualizado = Representante.objects.get(
            pessoa_fisica=self.pessoa_fisica, pessoa_juridica=self.pessoa_juridica
        )
        self.assertEqual(representante_atualizado.cargo, "Gerente")

    def test_delete_representante(self):
        self.representante.delete()
        self.assertFalse(Representante.objects.filter(
            pessoa_fisica=self.pessoa_fisica, pessoa_juridica=self.pessoa_juridica
        ).exists())
