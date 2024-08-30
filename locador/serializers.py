from rest_framework import serializers
from .models import Locador

class LocadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locador
        fields = '__all__'
