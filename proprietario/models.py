from django.db import models
from core.models import Pessoa

class Proprietario(Pessoa):
    """
    Representa um proprietário, herdando de Pessoa e adicionando
    informações específicas como data de nascimento e preferência de comunicação.
    """

    def __str__(self):
        return f"{self.nome} (Proprietário)"


class Representante(Pessoa):
    """
    Representa um representante legal de um proprietário, herdando de Pessoa.
    """
    
    def __str__(self):
        return f"{self.nome} (Representante)"



