from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# Configuração do schema view para documentação Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="PropertyHub API",
        default_version='v1',
        description="Documentação da API do PropertyHub",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Rota do Django Admin
    path('api/v1/', include('usuario.urls')),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Documentação Swagger
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include('locatario.urls')),
    path('api/v1/', include('locador.urls')),
    path('api/v1/', include('core.urls')), # inclui a rotas para os estados
    path('api/v1/', include('procuracao.urls')), # inclui rotas para procuracao
    path('api/v1/', include('documentacao.urls')),  # Inclui as URLs do app documentacao
    path('api/v1/', include('kanban.urls')),  # Inclui as URLs do app Kanban
    path('api/v1/', include('imovel.urls'))
]