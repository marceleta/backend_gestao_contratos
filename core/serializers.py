from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import PessoaFisica, PessoaJuridica, Representante, Telefone, Estado

class TelefoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Telefone
        fields = ['numero', 'tipo']


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ['id','sigla', 'nome']


class PessoaFisicaSerializer(serializers.ModelSerializer):
    telefones = TelefoneSerializer(many=True)

    class Meta:
        model = PessoaFisica
        fields = [
            'nome', 'email', 'telefone', 'endereco', 'bairro', 'cidade', 
            'estado', 'cep', 'cpf', 'identidade', 'orgao_expeditor', 
            'cnh', 'orgao_expeditor_cnh', 'data_nascimento', 'estado_civil', 
            'nacionalidade', 'profissao', 'telefones'
        ]

    def create(self, validated_data):
        # Separar telefones e estado dos dados validados
        telefones = validated_data.pop('telefones')
        estado = validated_data.pop('estado')

        # Criar a instância de PessoaFisica usando descompactação de dicionário
        pessoa_fisica = PessoaFisica.objects.create(estado=estado, **validated_data)

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

        return pessoa_fisica

    
    def update(self, instance, validated_data):
        telefones = validated_data.pop('telefones', None)
        estado = validated_data.pop('estado', None)

        # Atualizando todos os campos usando setattr
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Atualizando o campo 'estado' separadamente se fornecido
        if estado:
            instance.estado = estado

        # Salvando a instância de PessoaFisica
        instance.save()

        # Gerenciar telefones associados
        if telefones is not None:
            content_type = ContentType.objects.get_for_model(PessoaFisica)
            # Deletar telefones antigos
            Telefone.objects.filter(content_type=content_type, object_id=instance.id).delete()
            # Criar novos telefones
            Telefone.objects.bulk_create([
                Telefone(tipo=telefone['tipo'], numero=telefone['numero'], content_type=content_type, object_id=instance.id)
                for telefone in telefones
            ])
        
        return instance
    


class PessoaJuridicaSerializer(serializers.ModelSerializer):
    telefones = TelefoneSerializer(many=True)
    

    class Meta:
        model = PessoaJuridica
        fields = [
            'nome', 'email', 'telefone', 'endereco', 'bairro', 'cidade', 
            'estado', 'cep', 'cnpj', 'data_fundacao', 'nome_fantasia', 
            'data_abertura', 'inscricao_estadual', 'natureza_juridica', 
            'atividade_principal_cnae', 'telefones'
        ]

    def create(self, validated_data):
        estado = validated_data.pop('estado')
        telefones = validated_data.pop('telefones')

        pessoa_juridica = PessoaJuridica.objects.create(estado=estado, **validated_data)

        content_type = ContentType.objects.get_for_model(PessoaJuridica)

        Telefone.objects.bulk_create([
            Telefone(
                numero=telefone['numero'],
                tipo=telefone['tipo'],
                content_type=content_type,
                object_id=pessoa_juridica.id
            ) for telefone in telefones
        ])

        return pessoa_juridica

    
    def update(self, instance, validated_data):
        estado = validated_data.pop('estado')
        telefones = validated_data.pop('telefones')

        for atrr, value in validated_data.items():
            setattr(instance, atrr, value)


        if estado:
            instance.estado = estado 

        instance.save()
        
        if telefones is not None:
            content_type = ContentType.objects.get_for_model(PessoaJuridica)
            Telefone.objects.filter(content_type=content_type, object_id=instance.id).delete()
            
            Telefone.objects.bulk_create([
                Telefone(tipo=telefone['tipo'],
                         numero=telefone['numero'],
                         content_type=content_type,
                         object_id=instance.id) for telefone in telefones
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
    




