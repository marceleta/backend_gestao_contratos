from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from locador.models import Locador
from core.models import PessoaFisica, PessoaJuridica, Estado

class LocadorTestCase(TestCase):

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

    def test_create_locador(self):
        content_type = ContentType.objects.get_for_model(PessoaFisica)
        locador = Locador.objects.create(content_type=content_type, object_id=self.pessoa_fisica.id)
        self.assertEqual(locador.content_object, self.pessoa_fisica)
        self.assertEqual(str(locador), f"Locador: {self.pessoa_fisica}")

    def test_read_locador(self):
        content_type = ContentType.objects.get_for_model(PessoaFisica)
        locador = Locador.objects.create(content_type=content_type, object_id=self.pessoa_fisica.id)
        locador_lido = Locador.objects.get(id=locador.id)
        self.assertEqual(locador_lido.content_object, self.pessoa_fisica)

    def test_update_locador(self):
        content_type = ContentType.objects.get_for_model(PessoaFisica)
        locador = Locador.objects.create(content_type=content_type, object_id=self.pessoa_fisica.id)
        self.pessoa_fisica.nome = "João Silva"
        self.pessoa_fisica.save()
        locador.refresh_from_db()
        self.assertEqual(locador.content_object.nome, "João Silva")

    def test_delete_locador(self):
        content_type = ContentType.objects.get_for_model(PessoaFisica)
        locador = Locador.objects.create(content_type=content_type, object_id=self.pessoa_fisica.id)
        locador_id = locador.id
        locador.delete()
        self.assertFalse(Locador.objects.filter(id=locador_id).exists())



