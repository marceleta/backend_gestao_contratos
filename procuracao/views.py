from rest_framework import viewsets
from .models import Procuracao
from .serializers import ProcuracaoSerializer

class ProcuracaoViewSet(viewsets.ModelViewSet):

    queryset = Procuracao.objects.all()
    serializer_class = ProcuracaoSerializer