from django.test import TestCase
from core.models import PessoaJuridica, Estado, Telefone, Endereco
from django.contrib.contenttypes.models import ContentType

class PessoaJuridicaModelTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        
        # Criando Pessoa Jurídica
        self.pessoa_juridica = PessoaJuridica.objects.create(
            nome="Empresa X",
            email="contato@empresax.com",
            cnpj="12.345.678/0001-99",
            data_fundacao="2000-01-01"
        )

        # Criando um telefone associado à PessoaJuridica
        self.content_type = ContentType.objects.get_for_model(PessoaJuridica)
        self.telefone = Telefone.objects.create(
            numero="(11) 99999-9999",
            tipo="Comercial",
            content_type=self.content_type,
            object_id=self.pessoa_juridica.id
        )

        # Criando um endereço associado à PessoaJuridica
        self.endereco = Endereco.objects.create(
            tipo_endereco="Comercial",
            rua="Av. Principal",
            numero="1000",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="12345-678",
            content_type=self.content_type,
            object_id=self.pessoa_juridica.id
        )

    def test_create_pessoa_juridica(self):
        """Testa se a criação de PessoaJuridica foi bem-sucedida."""
        self.assertEqual(self.pessoa_juridica.nome_fantasia, None)
        self.assertEqual(self.pessoa_juridica.nome, "Empresa X")
        self.assertEqual(self.pessoa_juridica.cnpj, "12.345.678/0001-99")

    def test_read_pessoa_juridica(self):
        """Testa se conseguimos buscar a PessoaJuridica pelo CNPJ."""
        pessoa_juridica_lida = PessoaJuridica.objects.get(cnpj="12.345.678/0001-99")
        self.assertEqual(pessoa_juridica_lida.nome, "Empresa X")

    def test_update_pessoa_juridica(self):
        """Testa se conseguimos atualizar os dados da PessoaJuridica."""
        self.pessoa_juridica.nome_fantasia = "Empresa X Ltda"
        self.pessoa_juridica.save()
        pessoa_juridica_atualizada = PessoaJuridica.objects.get(cnpj="12.345.678/0001-99")
        self.assertEqual(pessoa_juridica_atualizada.nome_fantasia, "Empresa X Ltda")

    def test_delete_pessoa_juridica(self):
        """Testa se conseguimos deletar a PessoaJuridica."""
        self.pessoa_juridica.delete()
        self.assertFalse(PessoaJuridica.objects.filter(cnpj="12.345.678/0001-99").exists())

    def test_pessoa_juridica_tem_telefone(self):
        """Testa se o telefone foi corretamente associado à PessoaJuridica."""
        self.assertEqual(self.pessoa_juridica.telefones.count(), 1)
        self.assertEqual(self.pessoa_juridica.telefones.first().numero, "(11) 99999-9999")

    def test_pessoa_juridica_tem_endereco(self):
        """Testa se o endereço foi corretamente associado à PessoaJuridica."""
        self.assertEqual(self.pessoa_juridica.enderecos.count(), 1)
        self.assertEqual(self.pessoa_juridica.enderecos.first().rua, "Av. Principal")


