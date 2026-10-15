from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Aqui embaixo nós vamos registrar as nossas futuras ViewSets (ex: Contas, Extrato, Transações)
# router.register(r'contas', ContaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]