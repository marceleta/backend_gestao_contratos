from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import PessoaFisica, PessoaJuridica, Representante, Telefone, Estado, Endereco

class TelefoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefone
        fields = ['numero', 'tipo']


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['id','sigla', 'nome']

class EnderecoSerializer(serializers.ModelSerializer):
    estado = serializers.PrimaryKeyRelatedField(queryset=Estado.objects.all())

    class Meta:
        model = Endereco
        fields = [
            'id', 'tipo_endereco', 'rua', 'numero', 'bairro', 'cidade', 'estado',
            'cep', 'latitude', 'longitude'
        ]
        extra_kwargs = {
            'latitude': {'required': False},
            'longitude': {'required': False},
            'tipo_endereco': {'required': False},
        }

    def create(self, validated_data):
        """
        Cria um objeto Endereco associado a uma entidade genérica.
        """
        return Endereco.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Atualiza um objeto Endereco, permitindo modificações parciais.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class PessoaFisicaSerializer(serializers.ModelSerializer):
    telefones = TelefoneSerializer(many=True)
    enderecos = EnderecoSerializer(many=True)

    class Meta:
        model = PessoaFisica
        fields = [
            'nome', 'email', 'cpf', 'identidade', 'orgao_expeditor', 
            'cnh', 'orgao_expeditor_cnh', 'data_nascimento', 'estado_civil', 
            'nacionalidade', 'profissao', 'telefones', 'enderecos'
        ]

    def create(self, validated_data):
        # Separar telefones e estado dos dados validados
        telefones = validated_data.pop('telefones')
        enderecos = validated_data.pop('enderecos')

        # Criar a instância de PessoaFisica usando descompactação de dicionário
        pessoa_fisica = PessoaFisica.objects.create(**validated_data)

        # Obter o content_type para PessoaFisica
        content_type = ContentType.objects.get_for_model(PessoaFisica)

        # Criar todos os telefones de uma vez usando bulk_create
        Telefone.objects.bulk_create([
            Telefone(
                numero=telefone['numero'],
                tipo=telefone['tipo'],
                content_type=content_type,
                object_id=pessoa_fisica.id
            ) for telefone in telefones
        ])

        #Cria todos os endereços de uma vez
        Endereco.objects.bulk_create([
            Endereco(
                tipo_endereco=endereco['tipo_endereco'],
                rua=endereco['rua'],
                numero=endereco['numero'],
                bairro=endereco['bairro'],
                cidade=endereco['cidade'],
                estado=endereco['estado'],
                cep=endereco['cep'],
                latitude=endereco.get('latitude'),
                longitude=endereco.get('longitude'),
                content_type=content_type,
                object_id=pessoa_fisica.id

            ) for endereco in enderecos 
        ])

        return pessoa_fisica

    
    def update(self, instance, validated_data):
        telefones = validated_data.pop('telefones', None)
        enderecos = validated_data.pop('enderecos', None)

        # Atualizando todos os campos usando setattr
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Salvando a instância de PessoaFisica
        instance.save()

        content_type = ContentType.objects.get_for_model(PessoaFisica)

        if telefones is not None:
            Telefone.objects.filter(content_type=content_type, object_id=instance.id).delete()
            Telefone.objects.bulk_create([
                Telefone(
                    tipo=telefone['tipo'], 
                    numero=telefone['numero'], 
                    content_type=content_type, 
                    object_id=instance.id
                ) for telefone in telefones
            ])

        if enderecos is not None:
            Endereco.objects.filter(content_type=content_type, object_id=instance.id).delete()
            Endereco.objects.bulk_create([
                Endereco(
                    tipo_endereco=endereco['tipo_endereco'],
                    rua=endereco['rua'],
                    numero=endereco['numero'],
                    bairro=endereco['bairro'],
                    cidade=endereco['cidade'],
                    estado=endereco['estado'],
                    cep=endereco['cep'],
                    latitude=endereco.get('latitude'),
                    longitude=endereco.get('longitude'),
                    content_type=content_type,
                    object_id=instance.id
                ) for endereco in enderecos
            ])
        
        return instance
    

class PessoaJuridicaSerializer(serializers.ModelSerializer):
    telefones = TelefoneSerializer(many=True)
    enderecos = EnderecoSerializer(many=True)

    class Meta:
        model = PessoaJuridica
        fields = [
            'nome', 'email', 'cnpj', 'data_fundacao', 'nome_fantasia', 
            'data_abertura', 'inscricao_estadual', 'natureza_juridica', 
            'atividade_principal_cnae', 'telefones', 'enderecos'
        ]

    def create(self, validated_data):
        """Cria uma PessoaJuridica e associa telefones e endereços."""
        telefones_data = validated_data.pop('telefones', [])
        enderecos_data = validated_data.pop('enderecos', [])

        # Criando a instância de PessoaJuridica
        pessoa_juridica = PessoaJuridica.objects.create(**validated_data)

        # Obtendo ContentType para PessoaJuridica
        content_type = ContentType.objects.get_for_model(PessoaJuridica)

        # Criando Telefones
        Telefone.objects.bulk_create([
            Telefone(
                numero=telefone['numero'],
                tipo=telefone['tipo'],
                content_type=content_type,
                object_id=pessoa_juridica.id
            ) for telefone in telefones_data
        ])

        # Criando Endereços
        Endereco.objects.bulk_create([
            Endereco(
                tipo_endereco=endereco.get('tipo_endereco'),
                rua=endereco['rua'],
                numero=endereco['numero'],
                bairro=endereco['bairro'],
                cidade=endereco['cidade'],
                estado=endereco['estado'],
                cep=endereco['cep'],
                latitude=endereco.get('latitude'),
                longitude=endereco.get('longitude'),
                content_type=content_type,
                object_id=pessoa_juridica.id
            ) for endereco in enderecos_data
        ])

        return pessoa_juridica

    def update(self, instance, validated_data):
        """Atualiza uma PessoaJuridica, gerenciando telefones e endereços."""
        telefones_data = validated_data.pop('telefones', None)
        enderecos_data = validated_data.pop('enderecos', None)

        # Atualizando os campos normais
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        content_type = ContentType.objects.get_for_model(PessoaJuridica)

        # Atualizando Telefones
        if telefones_data is not None:
            Telefone.objects.filter(content_type=content_type, object_id=instance.id).delete()
            Telefone.objects.bulk_create([
                Telefone(
                    tipo=telefone['tipo'],
                    numero=telefone['numero'],
                    content_type=content_type,
                    object_id=instance.id
                ) for telefone in telefones_data
            ])

        # Atualizando Endereços
        if enderecos_data is not None:
            Endereco.objects.filter(content_type=content_type, object_id=instance.id).delete()
            Endereco.objects.bulk_create([
                Endereco(
                    tipo_endereco=endereco.get('tipo_endereco'),
                    rua=endereco['rua'],
                    numero=endereco['numero'],
                    bairro=endereco['bairro'],
                    cidade=endereco['cidade'],
                    estado=endereco['estado'],
                    cep=endereco['cep'],
                    latitude=endereco.get('latitude'),
                    longitude=endereco.get('longitude'),
                    content_type=content_type,
                    object_id=instance.id
                ) for endereco in enderecos_data
            ])

        return instance



class RepresentanteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Representante
        fields = ['pessoa_fisica', 'pessoa_juridica', 'cargo', 'nivel_autoridade']


    def create(self, validated_data):
        # Extrair os dados aninhados
        pessoa_fisica = validated_data.pop('pessoa_fisica')
        pessoa_juridica = validated_data.pop('pessoa_juridica')
        # Recuperar as instâncias existentes do banco de dados usando os IDs fornecidos
        pessoa_fisica = PessoaFisica.objects.get(id=pessoa_fisica.id)
        pessoa_juridica = PessoaJuridica.objects.get(id=pessoa_juridica.id)

        # Criar a instância de Representante
        representante = Representante.objects.create(
            pessoa_fisica=pessoa_fisica,
            pessoa_juridica=pessoa_juridica,
            cargo=validated_data.pop('cargo'),
            nivel_autoridade=validated_data.pop('nivel_autoridade')
        )

        return representante
    




