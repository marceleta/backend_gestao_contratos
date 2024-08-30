from django.test import TestCase
from core.models import PessoaJuridica, Estado

class PessoaJuridicaModelTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
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

    def test_create_pessoa_juridica(self):
        self.assertEqual(self.pessoa_juridica.nome_fantasia, None)
        self.assertEqual(self.pessoa_juridica.nome, "Empresa X")

    def test_read_pessoa_juridica(self):
        pessoa_juridica_lida = PessoaJuridica.objects.get(cnpj="12.345.678/0001-99")
        self.assertEqual(pessoa_juridica_lida.nome, "Empresa X")

    def test_update_pessoa_juridica(self):
        self.pessoa_juridica.nome_fantasia = "Empresa X Ltda"
        self.pessoa_juridica.save()
        pessoa_juridica_atualizada = PessoaJuridica.objects.get(cnpj="12.345.678/0001-99")
        self.assertEqual(pessoa_juridica_atualizada.nome_fantasia, "Empresa X Ltda")

    def test_delete_pessoa_juridica(self):
        self.pessoa_juridica.delete()
        self.assertFalse(PessoaJuridica.objects.filter(cnpj="12.345.678/0001-99").exists())

