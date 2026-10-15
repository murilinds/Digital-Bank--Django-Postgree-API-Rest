from rest_framework import serializers
from .models import ContaBancaria, Transacao

class ContaBancariaSerializer(serializers.ModelSerializer):
    # O ModelSerializer automatiza a conversão dos campos do nosso model
    # Mostramos também o username do usuário em vez de apenas o ID numérico
    usuario_nome = serializers.ReadOnlyField(source='usuario.username')

    class Meta:
        model = ContaBancaria
        fields = ['id', 'usuario', 'usuario_nome', 'saldo', 'criada_em']


class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = ['id', 'conta_origem', 'conta_destino', 'valor', 'tipo', 'data_transacao']