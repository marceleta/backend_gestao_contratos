from django.contrib import admin
from .models import Usuario
from django.contrib.auth.admin import UserAdmin


@admin.register(Usuario)
class CustomUsuarioAdmin(UserAdmin):
    pass
