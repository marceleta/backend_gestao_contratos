from core.models import Pessoa

class Locatario(Pessoa):
    """
    Representa um locatário, que é a pessoa que aluga um imóvel.
    Herdado da classe Pessoa, contém informações como nome, CPF,
    telefone, email, endereço, etc.
    """

    def __str__(self):
        return f"{self.nome} (Locatário)"
