from django.test import SimpleTestCase
from django.urls import reverse, resolve
from proprietario.views import ProprietarioViewSet

class TestUrls(SimpleTestCase):

    def test_proprietario_list_url_resolves(self):
        url = reverse('proprietario-list')
        self.assertEqual(resolve(url).func.cls, ProprietarioViewSet)

    def test_proprietario_detail_url_resolves(self):
        url = reverse('proprietario-detail', args=[1])
        self.assertEqual(resolve(url).func.cls, ProprietarioViewSet)