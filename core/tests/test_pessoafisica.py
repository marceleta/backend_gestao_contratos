from django.test import TestCase
from core.models import PessoaFisica, Estado, Telefone, Endereco
from django.contrib.contenttypes.models import ContentType

class PessoaFisicaModelTest(TestCase):

    def setUp(self):
        self.estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        
        # Criando Pessoa Física
        self.pessoa_fisica = PessoaFisica.objects.create(
            nome="João da Silva",
            email="joao@example.com",
            cpf="123.456.789-00",
            identidade="MG-12.345.678",
            orgao_expeditor="SSP-MG",
            data_nascimento="1980-01-01",
            estado_civil="Solteiro(a)",
            nacionalidade="Brasileiro"
        )

        # Criando um telefone associado à PessoaFisica
        self.content_type = ContentType.objects.get_for_model(PessoaFisica)
        self.telefone = Telefone.objects.create(
            numero="(11) 99999-9999",
            tipo="Celular",
            content_type=self.content_type,
            object_id=self.pessoa_fisica.id
        )

        # Criando um endereço associado à PessoaFisica
        self.endereco = Endereco.objects.create(
            tipo_endereco="Residencial",
            rua="Rua A",
            numero="123",
            bairro="Centro",
            cidade="São Paulo",
            estado=self.estado,
            cep="12345-678",
            content_type=self.content_type,
            object_id=self.pessoa_fisica.id
        )

    def test_create_pessoa_fisica(self):
        """Testa se a criação de PessoaFisica foi bem-sucedida."""
        self.assertEqual(self.pessoa_fisica.nome, "João da Silva")
        self.assertEqual(self.pessoa_fisica.cpf, "123.456.789-00")

    def test_read_pessoa_fisica(self):
        """Testa se conseguimos buscar a PessoaFisica pelo CPF."""
        pessoa_fisica_lida = PessoaFisica.objects.get(cpf="123.456.789-00")
        self.assertEqual(pessoa_fisica_lida.nome, "João da Silva")

    def test_update_pessoa_fisica(self):
        """Testa se conseguimos atualizar os dados da PessoaFisica."""
        self.pessoa_fisica.nome = "João Silva"
        self.pessoa_fisica.save()
        pessoa_fisica_atualizada = PessoaFisica.objects.get(cpf="123.456.789-00")
        self.assertEqual(pessoa_fisica_atualizada.nome, "João Silva")

    def test_delete_pessoa_fisica(self):
        """Testa se conseguimos deletar a PessoaFisica."""
        self.pessoa_fisica.delete()
        self.assertFalse(PessoaFisica.objects.filter(cpf="123.456.789-00").exists())

    def test_pessoa_fisica_tem_telefone(self):
        """Testa se o telefone foi corretamente associado à PessoaFisica."""
        self.assertEqual(self.pessoa_fisica.telefones.count(), 1)
        self.assertEqual(self.pessoa_fisica.telefones.first().numero, "(11) 99999-9999")

    def test_pessoa_fisica_tem_endereco(self):
        """Testa se o endereço foi corretamente associado à PessoaFisica."""
        self.assertEqual(self.pessoa_fisica.enderecos.count(), 1)
        self.assertEqual(self.pessoa_fisica.enderecos.first().rua, "Rua A")



