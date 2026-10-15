from django.contrib.auth.models import User
from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from decimal import Decimal

from .models import ContaBancaria, Transacao
from .serializers import ContaBancariaSerializer, TransacaoSerializer

# --- Views para renderizar as páginas HTML ---
def home_view(request):
    return render(request, 'contas/home.html')

def login_view(request):
    return render(request, 'contas/login.html')

def dashboard_view(request):
    return render(request, 'contas/dashboard.html')


# --- Endpoints da API REST ---

class ContaBancariaViewSet(viewsets.ModelViewSet):
    queryset = ContaBancaria.objects.all()
    serializer_class = ContaBancariaSerializer

@method_decorator(csrf_exempt, name='dispatch')
class TransacaoViewSet(viewsets.ModelViewSet):
    queryset = Transacao.objects.all()
    serializer_class = TransacaoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        conta_origem_id = data.get('conta_origem')
        conta_destino_id = data.get('conta_destino')
        
        # Converte o valor recebido para Decimal com segurança
        try:
            valor = Decimal(str(data.get('valor', 0)))
        except:
            return Response({"erro": "Valor inválido."}, status=status.HTTP_400_BAD_REQUEST)

        tipo = data.get('tipo')

        if valor <= 0:
            return Response({"erro": "O valor da transação deve ser maior que zero."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                conta_origem = ContaBancaria.objects.select_for_update().get(id=conta_origem_id)

                if tipo == 'DEPOSITO':
                    conta_origem.saldo += valor
                    conta_origem.save()

                elif tipo == 'SAQUE':
                    if conta_origem.saldo < valor:
                        return Response({"erro": "Saldo insuficiente para realizar o saque."}, status=status.HTTP_400_BAD_REQUEST)
                    conta_origem.saldo -= valor
                    conta_origem.save()

                elif tipo == 'TRANSFERENCIA':
                    if not conta_destino_id:
                        return Response({"erro": "Conta de destino é obrigatória para transferências."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if conta_origem.saldo < valor:
                        return Response({"erro": "Saldo insuficiente para realizar a transferência."}, status=status.HTTP_400_BAD_REQUEST)
                    
                    conta_destino = ContaBancaria.objects.select_for_update().get(id=conta_destino_id)
                    
                    conta_origem.saldo -= valor
                    conta_origem.save()
                    
                    conta_destino.saldo += valor
                    conta_destino.save()
                else:
                    return Response({"erro": "Tipo de transação inválido."}, status=status.HTTP_400_BAD_REQUEST)

                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ContaBancaria.DoesNotExist:
            return Response({"erro": "Conta de origem ou destino não encontrada."}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class CriarUsuarioView(APIView):
    authentication_classes = []  # Desativa a autenticação por sessão e o controlo CSRF
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"erro": "Utilizador e palavra-passe são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"erro": "Este nome de utilizador já existe."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                novo_usuario = User.objects.create_user(username=username, password=password)
                nova_conta = ContaBancaria.objects.create(usuario=novo_usuario, saldo=0.00)

                return Response({
                    "mensagem": "Conta criada com sucesso!",
                    "conta_id": nova_conta.id,
                    "usuario": novo_usuario.username
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)