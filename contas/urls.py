from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContaBancariaViewSet, TransacaoViewSet, dashboard_view, CriarUsuarioView

router = DefaultRouter()
router.register(r'api/contas', ContaBancariaViewSet)
router.register(r'api/transacoes', TransacaoViewSet)

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('api/registrar/', CriarUsuarioView.as_view(), name='api-registrar'), # Atualizado para .as_view()
    path('', include(router.urls)),
]