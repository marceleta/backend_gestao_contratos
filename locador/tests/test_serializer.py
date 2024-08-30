from django.test import TestCase
from locador.models import Locador
from locador.serializers import LocadorSerializer
from core.models import PessoaFisica, Estado
from django.contrib.contenttypes.models import ContentType

class LocadorSerializerTestCase(TestCase):

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
        self.content_type = ContentType.objects.get_for_model(PessoaFisica)
        self.locador_data = {
            'content_type': self.content_type.id,
            'object_id': self.pessoa_fisica.id
        }

    def test_create_locador(self):
        serializer = LocadorSerializer(data=self.locador_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        locador = serializer.save()
        self.assertEqual(locador.content_object, self.pessoa_fisica)


    def test_read_locador(self):
        locador = Locador.objects.create(content_type=self.content_type, object_id=self.pessoa_fisica.id)
        serializer = LocadorSerializer(locador)
        self.assertEqual(serializer.data['object_id'], self.pessoa_fisica.id)
        self.assertEqual(serializer.data['content_type'], self.content_type.id)

    def test_update_locador(self):
        locador = Locador.objects.create(content_type=self.content_type, object_id=self.pessoa_fisica.id)
        nova_pessoa_fisica = PessoaFisica.objects.create(
            nome="Maria Silva",
            email="maria@example.com",
            telefone="12345-6799",
            endereco="Rua B",
            bairro="Centro",
            cidade="Rio de Janeiro",
            estado=self.estado,
            cep="12345-679",
            cpf="123.456.789-01",
            identidade="RJ-12.345.679",
            orgao_expeditor="SSP-RJ",
            data_nascimento="1990-01-01",
            estado_civil="Casado(a)",
            nacionalidade="Brasileiro"
        )
        nova_content_type = ContentType.objects.get_for_model(PessoaFisica)
        nova_locador_data = {
            'content_type': nova_content_type.id,
            'object_id': nova_pessoa_fisica.id
        }
        serializer = LocadorSerializer(locador, data=nova_locador_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        locador_atualizado = serializer.save()
        self.assertEqual(locador_atualizado.content_object, nova_pessoa_fisica)

    def test_delete_locador(self):
        locador = Locador.objects.create(content_type=self.content_type, object_id=self.pessoa_fisica.id)
        locador_id = locador.id
        locador.delete()
        self.assertFalse(Locador.objects.filter(id=locador_id).exists())



