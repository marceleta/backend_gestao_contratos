from django.test import TestCase
from core.models import Estado

class EstadoModelTest(TestCase):
    def test_create_estado(self):
        estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        self.assertEqual(estado.sigla, "SP")
        self.assertEqual(estado.nome, "São Paulo")

    def test_read_estado(self):
        estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        estado_lido = Estado.objects.get(sigla="SP")
        self.assertEqual(estado_lido.nome, "São Paulo")

    def test_update_estado(self):
        estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        estado.nome = "Rio de Janeiro"
        estado.save()
        self.assertEqual(Estado.objects.get(sigla="SP").nome, "Rio de Janeiro")

    def test_delete_estado(self):
        estado = Estado.objects.create(sigla="SP", nome="São Paulo")
        estado.delete()
        self.assertFalse(Estado.objects.filter(sigla="SP").exists())
