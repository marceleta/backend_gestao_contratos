import random
from locatario.models import Locatario
from core.models import Telefone, Estado
from django.contrib.contenttypes.models import ContentType

# Supondo que já existam Estados no banco de dados
estados = list(Estado.objects.all())

# Lista de nomes reais
nomes = [
    "João Silva", "Maria Oliveira", "Pedro Santos", "Ana Souza",
    "Carlos Pereira", "Fernanda Lima", "Lucas Andrade", "Patrícia Souza",
    "Ricardo Alves", "Gabriela Ramos", "Paulo Henrique", "Juliana Carvalho",
    "Rafael Costa", "Larissa Silva", "Marcelo Mendes"
]

# Criação de 15 locatários com 1 ou 2 telefones
for i in range(15):
    nome = nomes[i]
    cpf = f"{i+1:03d}.456.789-0{i+1:01d}"
    identidade = f"{i+1:02d}3456789"
    orgao_expeditor = "SSP-SP"
    email = f"locatario{i+1}@email.com"
    endereco = f"Rua {i+1}, 123"
    bairro = "Centro"
    cidade = "Cidade Exemplo"
    cep = "01000-000"
    nacionalidade = "Brasileiro"
    data_nascimento = "1985-05-20"
    estado_civil = random.choice(["Solteiro(a)", "Casado(a)", "Divorciado(a)"])
    preferencia_comunicacao = random.choice(["Email", "Telefone", "WhatsApp"])
    estado = random.choice(estados)

    # Criando o locatário
    locatario = Locatario.objects.create(
        nome=nome,
        cpf=cpf,
        identidade=identidade,
        orgao_expeditor=orgao_expeditor,
        email=email,
        endereco=endereco,
        bairro=bairro,
        cidade=cidade,
        cep=cep,
        nacionalidade=nacionalidade,
        data_nascimento=data_nascimento,
        estado_civil=estado_civil,
        preferencia_comunicacao=preferencia_comunicacao,
        estado=estado,
    )

    # Associando de 1 a 2 telefones ao locatário
    content_type = ContentType.objects.get_for_model(Locatario)
    for j in range(random.randint(1, 2)):
        Telefone.objects.create(
            pessoa=locatario,
            numero=f"{random.randint(10, 99)}{random.randint(90000, 99999)}-{random.randint(1000, 9999)}",
            tipo=random.choice(["Celular", "Residencial"]),
            content_type=content_type,
            object_id=locatario.id
        )

print("15 locatários com 1 a 2 telefones cada foram criados.")