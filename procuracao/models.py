from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

class Procuracao(models.Model):
    outorgante_content_type = models.ForeignKey(ContentType, related_name='outorgante_content_type', on_delete=models.CASCADE)
    outorgante_object_id = models.PositiveIntegerField()
    outorgante = GenericForeignKey('outorgante_content_type', 'outorgante_object_id')

    outorgado_content_type = models.ForeignKey(ContentType, related_name='outorgado_content_type', on_delete=models.CASCADE)
    outorgado_object_id = models.PositiveIntegerField()
    outorgado = GenericForeignKey('outorgado_content_type', 'outorgado_object_id')

    data_inicio = models.DateField()
    data_validade = models.DateField()
    escopo = models.CharField(max_length=255, help_text="Escopo da procuração, por exemplo, 'Locação de imóvel'.")
    documento = models.FileField(upload_to='procuracoes/', help_text="Upload do documento da procuração em PDF.")

    def __str__(self):
        return f"Procuração de {self.outorgante} para {self.outorgado}"
