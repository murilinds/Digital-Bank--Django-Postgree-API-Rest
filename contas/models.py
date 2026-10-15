from django.db import models
from django.contrib.auth.models import User

class ContaBancaria(models.Model):
    # OneToOneField: Garante que cada usuário do sistema tem exatamente uma conta bancária.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='conta')
    
    # DecimalField: OBRIGATÓRIO para dinheiro! Nunca use float. 
    # max_digits=12 (tamanho total do número) e decimal_places=2 (os centavos).
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conta de {self.usuario.username} - Saldo: R$ {self.saldo}"


class Transacao(models.Model):
    TIPO_CHOICES = (
        ('DEPOSITO', 'Depósito'),
        ('SAQUE', 'Saque'),
        ('TRANSFERENCIA', 'Transferência'),
    )

    # ForeignKey (Chave Estrangeira): A conta de quem está enviando ou fazendo a operação.
    conta_origem = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE, related_name='transacoes_enviadas')
    
    # Conta de destino: Usada apenas em transferências (pode ficar vazia/null em saques e depósitos).
    conta_destino = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE, null=True, blank=True, related_name='transacoes_recebidas')
    
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_transacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} de R$ {self.valor} - Origem: {self.conta_origem.usuario.username}"
# Create your models here.
