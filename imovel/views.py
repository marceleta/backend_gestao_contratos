from rest_framework import viewsets, status
from rest_framework.response import Response
from imovel.models import Imovel, SituacaoFiscal, TransacaoImovel
from imovel.serializers import ImovelSerializer, TransacaoImovelSerializer, SituacaoFiscalSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

class ImovelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Imóveis.

    Este ViewSet permite realizar operações CRUD para o modelo Imovel.
    """
    queryset = Imovel.objects.all().order_by('id')
    serializer_class = ImovelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada do Imovel
        #print('request.data: '+str(request.data))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        imovel = serializer.save()
        return Response(
            ImovelSerializer(imovel).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada do Imovel
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        imovel = serializer.save()
        return Response(
            ImovelSerializer(imovel).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção do Imovel
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        imovel = get_object_or_404(Imovel, pk=pk)
        serializer = ImovelSerializer(imovel)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        # Verifica se um parâmetro de filtro foi enviado
        nome = request.query_params.get('nome', None)
        cidade = request.query_params.get('cidade', None)

        queryset = self.get_queryset()

        # Aplica os filtros de acordo com os parâmetros do request
        if nome:
            queryset = queryset.filter(nome__icontains=nome)
        if cidade:
            queryset = queryset.filter(cidade__icontains=cidade)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SituacaoFiscalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Situações Fiscais.

    Este ViewSet permite realizar operações CRUD para o modelo SituacaoFiscal.
    """
    queryset = SituacaoFiscal.objects.all().order_by('id')
    serializer_class = SituacaoFiscalSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada de Situação Fiscal
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        situacao_fiscal = serializer.save()
        return Response(
            SituacaoFiscalSerializer(situacao_fiscal).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada de Situação Fiscal
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        situacao_fiscal = serializer.save()
        return Response(
            SituacaoFiscalSerializer(situacao_fiscal).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção de Situação Fiscal
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        situacao_fiscal = get_object_or_404(SituacaoFiscal, pk=pk)
        serializer = SituacaoFiscalSerializer(situacao_fiscal)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        imovel_id = request.query_params.get('imovel_id', None)
        queryset = self.get_queryset()

        if imovel_id:
            queryset = queryset.filter(imovel_id=imovel_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    # Método customizado para retornar as opções de SITUACAO_FISCAL_CHOICES
    @action(detail=False, methods=['get'], url_path='situacao-fiscal-choices')
    def situacao_fiscal_choices(self, request):
        """
        Retorna os valores de SITUACAO_FISCAL_CHOICES.
        """
        choices = SituacaoFiscal.SITUACAO_FISCAL_CHOICES
        return Response(choices, status=status.HTTP_200_OK)
    

class TransacaoImovelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Transações de Imóvel.

    Este ViewSet permite realizar operações CRUD para o modelo TransacaoImovel.
    """
    queryset = TransacaoImovel.objects.all().order_by('id')
    serializer_class = TransacaoImovelSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada de Transação Imobiliária
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transacao = serializer.save()
        return Response(
            TransacaoImovelSerializer(transacao).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada de Transação Imobiliária
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        transacao = serializer.save()
        return Response(
            TransacaoImovelSerializer(transacao).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção de Transação Imobiliária
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs['pk']
        transacao = get_object_or_404(TransacaoImovel, pk=pk)
        serializer = TransacaoImovelSerializer(transacao)
        return Response(serializer.data)
    
    def list(self, request, *args, **kwargs):
        imovel_id = request.query_params.get('imovel_id', None)
        queryset = self.get_queryset()

        if imovel_id:
            queryset = queryset.filter(imovel_id=imovel_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'], url_path='tipo-transacao-choices')
    def tipo_transacao_choices(self, request):
        """
        Retorna as opções de tipo_transacao disponíveis para o frontend.
        """
        choices = TransacaoImovel.TIPO_TRANSACAO_CHOICES
        response_data = [{"value": key, "label": label} for key, label in choices]
        return Response(response_data, status=status.HTTP_200_OK)


