from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import DocumentoPessoaFisica, DocumentoPessoaJuridica
from .serializers import DocPessoaFisicaSerializer, DocPessoaJuridicaSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class DocPessoaFisicaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar documentos de Pessoa Física.

    Este ViewSet permite realizar operações CRUD para o modelo DocumentoPessoaFisica.
    """
    queryset = DocumentoPessoaFisica.objects.all().order_by('id')
    serializer_class = DocPessoaFisicaSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada do DocumentoPessoaFisica
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        documento = serializer.save()
        return Response(
            DocPessoaFisicaSerializer(documento).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada do DocumentoPessoaFisica
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        documento = serializer.save()
        return Response(
            DocPessoaFisicaSerializer(documento).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção do DocumentoPessoaFisica
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        #queryset = self.queryset.get(id=pk)
        #print(str(queryset))
        documento = get_object_or_404(DocumentoPessoaFisica, pk=kwargs['pk'])
        serializer = DocPessoaFisicaSerializer(documento)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):

        pessoa_fisica_id = request.query_params.get('pessoa_fisica', None)
        queryset = self.get_queryset().filter(pessoa_fisica_id=pessoa_fisica_id)
        #print("QuerySet: "+str(queryset))
        page = self.paginate_queryset(queryset)
        #print(str(page))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

class DocPessoaJuridicaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar documentos de Pessoa Jurídica.

    Este ViewSet permite realizar operações CRUD para o modelo DocumentoPessoaJuridica.
    """
    queryset = DocumentoPessoaJuridica.objects.all().order_by('id')
    serializer_class = DocPessoaJuridicaSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada do DocumentoPessoaJuridica
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        documento = serializer.save()
        return Response(
            DocPessoaJuridicaSerializer(documento).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada do DocumentoPessoaJuridica
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        documento = serializer.save()
        return Response(
            DocPessoaJuridicaSerializer(documento).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção do DocumentoPessoaJuridica
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        documento = get_object_or_404(DocumentoPessoaJuridica, pk=pk)
        serializer = DocPessoaJuridicaSerializer(documento)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        pessoa_juridica_id = request.query_params.get('pessoa_juridica', None)
        queryset = self.get_queryset()
        
        if pessoa_juridica_id is not None:
            queryset = queryset.filter(pessoa_juridica_id=pessoa_juridica_id)
        
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


