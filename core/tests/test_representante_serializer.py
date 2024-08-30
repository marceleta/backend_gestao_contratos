from django.test import TestCase
from core.models import Representante, PessoaFisica, PessoaJuridica, Estado, Telefone
from core.serializers import PessoaFisicaSerializer, PessoaJuridicaSerializer
from core.serializers import RepresentanteSerializer
from django.contrib.contenttypes.models import ContentType

class RepresentanteSerializerTestCase(TestCase):

    def setUp(self):
        self.estado_sp = Estado.objects.create(id=1, sigla='SP', nome='São Paulo')
        self.estado_rj = Estado.objects.create(id=2, sigla='RJ', nome='Rio de Janeiro')

        self.pessoa_fisica = PessoaFisica.objects.create(
            nome='João da Silva',
            email='joao@example.com',
            telefone='12345-6789',
            endereco='Rua A',
            bairro='Centro',
            cidade='São Paulo',
            estado=self.estado_sp,
            cep='12345-678',
            cpf='123.456.789-00',
            identidade='MG-12.345.678',
            orgao_expeditor='SSP-MG',
            data_nascimento='1980-01-01',
            estado_civil='Solteiro(a)',
            nacionalidade='Brasileiro'
        )

        self.pessoa_juridica = PessoaJuridica.objects.create(
            nome='Empresa ABC',
            email='empresa@example.com',
            telefone='12345-6789',
            endereco='Rua B',
            bairro='Centro',
            cidade='São Paulo',
            estado=self.estado_rj,
            cep='12345-678',
            cnpj='12.345.678/0001-00',
            data_fundacao='2000-01-01',
            nome_fantasia='Fantasia ABC',
            inscricao_estadual='123456789',
            natureza_juridica='Sociedade Anônima',
            atividade_principal_cnae='62.01-1-00'
        )

        # Criação de telefones para Pessoa Física
        content_type_fisica = ContentType.objects.get_for_model(self.pessoa_fisica)
        Telefone.objects.create(content_type=content_type_fisica, object_id=self.pessoa_fisica.id, numero='12345-6789', tipo='Residencial')
        Telefone.objects.create(content_type=content_type_fisica, object_id=self.pessoa_fisica.id, numero='98765-4321', tipo='Celular')

        # Criação de telefones para Pessoa Jurídica
        content_type_juridica = ContentType.objects.get_for_model(self.pessoa_juridica)
        Telefone.objects.create(content_type=content_type_juridica, object_id=self.pessoa_juridica.id, numero='12345-6789', tipo='Comercial')
        Telefone.objects.create(content_type=content_type_juridica, object_id=self.pessoa_juridica.id, numero='98765-4321', tipo='Whatsapp')

        self.representante = Representante.objects.create(pessoa_fisica=self.pessoa_fisica, 
                                                          pessoa_juridica=self.pessoa_juridica,
                                                          cargo='Gerente', nivel_autoridade='Supervisor')
        

    def test_create_representante(self):
        data = {
            'pessoa_fisica': self.pessoa_fisica.id,
            'pessoa_juridica':self.pessoa_juridica.id,
            'cargo': 'Gerente',
            'nivel_autoridade': 'Supervisor'
        }
        serializer = RepresentanteSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        representante = serializer.save()
        self.assertEqual(representante.cargo, 'Gerente')
        self.assertEqual(representante.nivel_autoridade, 'Supervisor')

    def test_read_representante(self):
        serializer = RepresentanteSerializer(self.representante)
        data = serializer.data
        #print(data)
        self.assertEqual(data['pessoa_fisica'], self.pessoa_fisica.id)
        self.assertEqual(data['pessoa_juridica'], self.pessoa_juridica.id)
        self.assertEqual(data['cargo'], 'Gerente')
        self.assertEqual(data['nivel_autoridade'], 'Supervisor')

    def test_update_representante(self):
        data = {
            'cargo': 'Diretor',
            'nivel_autoridade': 'Gerente'
        }
        serializer = RepresentanteSerializer(self.representante, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        representante = serializer.save()
        self.assertEqual(representante.cargo, 'Diretor')
        self.assertEqual(representante.nivel_autoridade, 'Gerente')

    def test_delete_representante(self):
        representante_id = self.representante.id
        self.representante.delete()
        with self.assertRaises(Representante.DoesNotExist):
            Representante.objects.get(id=representante_id)


    def test_update_pessoa_fisica_no_representante(self):
        # Cria uma nova pessoa física
        nova_pessoa_fisica = PessoaFisica.objects.create(
            nome='Carlos Pereira',
            email='carlos@example.com',
            telefone='99999-9999',
            endereco='Rua C',
            bairro='Jardim',
            cidade='Rio de Janeiro',
            estado=self.estado_rj,
            cep='87654-321',
            cpf='987.654.321-00',
            identidade='RJ-98.765.432',
            orgao_expeditor='SSP-RJ',
            data_nascimento='1975-02-02',
            estado_civil='Casado(a)',
            nacionalidade='Brasileiro'
        )

        data = {
            'pessoa_fisica': nova_pessoa_fisica.id,
            'pessoa_juridica': self.representante.pessoa_juridica.id,
            'cargo': self.representante.cargo,
            'nivel_autoridade': self.representante.nivel_autoridade
        }

        serializer = RepresentanteSerializer(self.representante, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        representante_atualizado = serializer.save()

        self.assertEqual(representante_atualizado.pessoa_fisica, nova_pessoa_fisica)

    def test_update_pessoa_juridica_no_representante(self):
        # Cria uma nova pessoa jurídica
        nova_pessoa_juridica = PessoaJuridica.objects.create(
            nome='Nova Empresa Ltda',
            email='contato@novaempresa.com',
            telefone='88888-8888',
            endereco='Av. Nova',
            bairro='Bairro Novo',
            cidade='São Paulo',
            estado=self.estado_sp,
            cep='65432-987',
            cnpj='98.765.432/0001-00',
            data_fundacao='2010-03-03',
            nome_fantasia='Nova Fantasia Ltda',
            inscricao_estadual='987654321',
            natureza_juridica='Sociedade Limitada',
            atividade_principal_cnae='70.20-4-00'
        )

        data = {
            'pessoa_fisica': self.representante.pessoa_fisica.id,
            'pessoa_juridica': nova_pessoa_juridica.id,
            'cargo': self.representante.cargo,
            'nivel_autoridade': self.representante.nivel_autoridade
        }

        serializer = RepresentanteSerializer(self.representante, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        representante_atualizado = serializer.save()

        self.assertEqual(representante_atualizado.pessoa_juridica, nova_pessoa_juridica)



