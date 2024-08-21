from django.db import models
from proprietario.models import Proprietario, Representante

class Procuracao(models.Model):
    """
    Representa uma procuração que permite a um representante atuar em nome de uma pessoa
    (proprietário ou inquilino) sobre determinado escopo e período.
    """
    outorgante = models.ForeignKey(Proprietario, related_name='procuracoes', on_delete=models.CASCADE)
    representante = models.ForeignKey(Representante, related_name='procuracoes_representante', on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_validade = models.DateField()
    escopo = models.CharField(max_length=255, help_text="Escopo da procuração, por exemplo, 'Locação de imóvel'.")
    documento = models.FileField(upload_to='procuracoes/', help_text="Upload do documento da procuração em PDF.")

    def __str__(self):
        return f"Procuração de {self.outorgante} para {self.representante}"
