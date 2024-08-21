from rest_framework import serializers
from .models import Procuracao


class ProcuracaoSerializer(serializers.ModelSerializer):

    class Meta:
            model = Procuracao
            fields = '__all__'

