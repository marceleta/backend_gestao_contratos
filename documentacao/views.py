from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import DocumentoPessoaFisica, DocumentoPessoaJuridica, DocumentoImovel, FotosVideoImovel
from .serializers import DocPessoaFisicaSerializer, DocPessoaJuridicaSerializer, DocImovelSerializer, FotosVideoImovelSerializer
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
    

class DocumentoImovelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar documentos de Imóvel.

    Este ViewSet permite realizar operações CRUD para o modelo DocumentoImovel.
    """
    queryset = DocumentoImovel.objects.all().order_by('id')
    serializer_class = DocImovelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada do DocumentoImovel
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        documento = serializer.save()
        return Response(
            DocImovelSerializer(documento).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada do DocumentoImovel
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        documento = serializer.save()
        return Response(
            DocImovelSerializer(documento).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção do DocumentoImovel
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        # Recuperação de um único documento
        pk = kwargs['pk']
        documento = get_object_or_404(DocumentoImovel, pk=pk)
        serializer = DocImovelSerializer(documento)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # Listagem de documentos filtrados por imovel (opcional)
        imovel_id = request.query_params.get('imovel', None)
        queryset = self.get_queryset()
        
        if imovel_id is not None:
            queryset = queryset.filter(imovel_id=imovel_id)
        
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FotosVideoImovelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar fotos e vídeos de Imóvel.

    Este ViewSet permite realizar operações CRUD para o modelo FotosVideoImovel.
    """
    queryset = FotosVideoImovel.objects.all().order_by('id')
    serializer_class = FotosVideoImovelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada de Foto/Video do Imóvel
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        midia = serializer.save()
        return Response(
            FotosVideoImovelSerializer(midia).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada de Foto/Video do Imóvel
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        midia = serializer.save()
        return Response(
            FotosVideoImovelSerializer(midia).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção de Foto/Video do Imóvel
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        # Recuperação de um único arquivo de mídia
        pk = kwargs['pk']
        midia = get_object_or_404(FotosVideoImovel, pk=pk)
        serializer = FotosVideoImovelSerializer(midia)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # Listagem de fotos e vídeos filtrados por imóvel (opcional)
        imovel_id = request.query_params.get('imovel', None)
        queryset = self.get_queryset()

        if imovel_id is not None:
            queryset = queryset.filter(imovel_id=imovel_id)

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



