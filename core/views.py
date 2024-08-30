from rest_framework import viewsets, permissions, pagination
from .models import Estado, Representante
from .serializers import EstadoSerializer
from rest_framework.permissions import IsAuthenticated
from .models import PessoaFisica, PessoaJuridica
from .serializers import PessoaFisicaSerializer, PessoaJuridicaSerializer, RepresentanteSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.db.models import Q
from itertools import chain
from rest_framework.pagination import PageNumberPagination


class EstadoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gerenciar Estado.

    Este ViewSet fornece as operações CRUD para o modelo Estado e está otimizado
    para minimizar o número de queries ao banco de dados usando `select_related`.
    Acesso restrito a usuários autenticados.
    """

    queryset = Estado.objects.all().order_by('nome') # Otimização do queryset
    serializer_class = EstadoSerializer
    permission_classes = [permissions.IsAuthenticated]  # Permissões de acesso


class ClientePagination(pagination.PageNumberPagination):
    page_size = 10  # Ajuste conforme necessário

class ClienteViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = ClientePagination

    def list(self, request):
        cache_key = 'combined_clients_results'
        combined_results = cache.get(cache_key)

        if not combined_results:
            # Obter todas as pessoas físicas e jurídicas
            pessoas_fisicas = PessoaFisica.objects.all().order_by('nome')
            pessoas_juridicas = PessoaJuridica.objects.all().order_by('nome')

            # Serializar os dados
            fisicas_serializer = PessoaFisicaSerializer(pessoas_fisicas, many=True)
            juridicas_serializer = PessoaJuridicaSerializer(pessoas_juridicas, many=True)

            # Combinar os resultados
            combined_results = fisicas_serializer.data + juridicas_serializer.data

            # Salvar no cache por 5 minutos (300 segundos)
            cache.set(cache_key, combined_results, timeout=300)

        # Paginar os resultados combinados
        page = self.paginate_queryset(combined_results, request)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(combined_results, status=status.HTTP_200_OK)
    

    def create(self, request):
        # Verifica o tipo de pessoa com base no JSON recebido
        if 'cpf' in request.data:
            # Tratamento para Pessoa Física
            serializer = PessoaFisicaSerializer(data=request.data)
            pessoa_type = "Pessoa Física"
        elif 'cnpj' in request.data:
            # Tratamento para Pessoa Jurídica
            serializer = PessoaJuridicaSerializer(data=request.data)
            pessoa_type = "Pessoa Jurídica"
        else:
            return Response({"error": "Dados inválidos. Necessário fornecer CPF para pessoa física ou CNPJ para pessoa jurídica."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validação e salvamento dos dados
        if serializer.is_valid():
            serializer.save()
            return Response({"message": f"{pessoa_type} criada com sucesso!", "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def retrieve(self, request, pk=None):
        # Verificar se o tipo de pessoa foi passado na requisição
        tipo_pessoa = request.query_params.get('tipo', None)
        
        if tipo_pessoa == 'fisica':
            # Tentar recuperar a pessoa física
            try:
                pessoa_fisica = PessoaFisica.objects.get(pk=pk)
                serializer = PessoaFisicaSerializer(pessoa_fisica)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PessoaFisica.DoesNotExist:
                return Response({"error": "Pessoa Física não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        elif tipo_pessoa == 'juridica':
            # Tentar recuperar a pessoa jurídica
            try:
                pessoa_juridica = PessoaJuridica.objects.get(pk=pk)
                serializer = PessoaJuridicaSerializer(pessoa_juridica)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except PessoaJuridica.DoesNotExist:
                return Response({"error": "Pessoa Jurídica não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({"error": "Tipo de pessoa não especificado ou inválido. Use 'fisica' ou 'juridica'."},
                            status=status.HTTP_400_BAD_REQUEST)
        


    def update(self, request, pk=None):
        # Verificar se o tipo de pessoa foi passado na requisição
        tipo_pessoa = request.query_params.get('tipo', None)
        
        if tipo_pessoa == 'fisica':
            # Tentar atualizar a pessoa física
            try:
                pessoa_fisica = PessoaFisica.objects.get(pk=pk)
                serializer = PessoaFisicaSerializer(pessoa_fisica, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except PessoaFisica.DoesNotExist:
                return Response({"error": "Pessoa Física não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        elif tipo_pessoa == 'juridica':
            # Tentar atualizar a pessoa jurídica
            try:
                pessoa_juridica = PessoaJuridica.objects.get(pk=pk)
                serializer = PessoaJuridicaSerializer(pessoa_juridica, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except PessoaJuridica.DoesNotExist:
                return Response({"error": "Pessoa Jurídica não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({"error": "Tipo de pessoa não especificado ou inválido. Use 'fisica' ou 'juridica'."},
                            status=status.HTTP_400_BAD_REQUEST)


    def search_by_nome(self, request):
        # Recebe o termo de busca da query params
        search_query = request.query_params.get('search', None)

        if not search_query:
            return Response({"error": "Termo de busca não fornecido."}, status=status.HTTP_400_BAD_REQUEST)

        # Busca nos modelos de PessoaFisica e PessoaJuridica
        pessoas_fisicas = PessoaFisica.objects.filter(
            Q(nome__icontains=search_query)
        ).order_by('nome')

        pessoas_juridicas = PessoaJuridica.objects.filter(
            Q(nome__icontains=search_query)
        ).order_by('nome')

        # Combine os querysets
        combined_querysets = list(chain(pessoas_fisicas, pessoas_juridicas))

        if not combined_querysets:
            return Response({"message": "Nenhum registro encontrado para o termo de busca fornecido."}, status=status.HTTP_404_NOT_FOUND)

        # Paginação
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(combined_querysets, request)
        if page is not None:
            # Serializa os dados paginados
            fisicas_serializer = PessoaFisicaSerializer(pessoas_fisicas, many=True)
            juridicas_serializer = PessoaJuridicaSerializer(pessoas_juridicas, many=True)

            combined_results = fisicas_serializer.data + juridicas_serializer.data
            return paginator.get_paginated_response(combined_results)

        # Se a paginação não for aplicada, serializa todos os dados
        fisicas_serializer = PessoaFisicaSerializer(pessoas_fisicas, many=True)
        juridicas_serializer = PessoaJuridicaSerializer(pessoas_juridicas, many=True)

        combined_results = fisicas_serializer.data + juridicas_serializer.data

        return Response(combined_results, status=status.HTTP_200_OK)


    

    def destroy(self, request, pk=None):
        # Verificar se o tipo de pessoa foi passado na requisição
        tipo_pessoa = request.query_params.get('tipo', None)
        
        if tipo_pessoa == 'fisica':
            try:
                pessoa_fisica = PessoaFisica.objects.get(pk=pk)
                pessoa_fisica.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except PessoaFisica.DoesNotExist:
                return Response({"error": "Pessoa Física não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        elif tipo_pessoa == 'juridica':
            try:
                pessoa_juridica = PessoaJuridica.objects.get(pk=pk)
                pessoa_juridica.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except PessoaJuridica.DoesNotExist:
                return Response({"error": "Pessoa Jurídica não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({"error": "Tipo de pessoa não especificado ou inválido. Use 'fisica' ou 'juridica'."},
                            status=status.HTTP_400_BAD_REQUEST)
        

class RepresentanteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Representantes.

    Este ViewSet permite realizar operações CRUD para o modelo Representante.
    """
    queryset = Representante.objects.all()
    serializer_class = RepresentanteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Criação personalizada do Representante
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        representante = serializer.save()
        return Response(
            RepresentanteSerializer(representante).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        # Atualização personalizada do Representante
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        representante = serializer.save()
        return Response(
            RepresentanteSerializer(representante).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        # Deleção do Representante
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)