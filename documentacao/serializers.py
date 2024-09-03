from rest_framework import serializers
from .models import DocumentoPessoaFisica, DocumentoPessoaJuridica
import os
from django.core.exceptions import ValidationError

class DocPessoaFisicaSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentoPessoaFisica
        fields = ['id', 'pessoa_fisica', 'tipo_documento', 'descricao', 'arquivo', 'data_emissao']

    def validate_arquivo(self, value):
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.pdf', '.docx', '.jpg', '.png']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Extensão de arquivo não suportada.')
        return value
    

class DocPessoaJuridicaSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentoPessoaJuridica
        fields = ['id', 'pessoa_juridica', 'tipo_documento', 'descricao', 'arquivo', 'data_emissao']

    def validate_arquivo(self, value):
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.pdf', '.docx', '.jpg', '.png']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Extensão de arquivo não suportada.')
        return value


