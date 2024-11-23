from django.db.models.signals import post_save
from django.dispatch import receiver
from usuario.models import Usuario
from kanban.models import criar_kanban_padrao

@receiver(post_save, sender=Usuario)
def criar_kanban_ao_criar_usuario(sender, instance, created, **kwargs):
    if created:
        # Cria o kanban padrão para o usuário recém-criado
        criar_kanban_padrao(instance)
