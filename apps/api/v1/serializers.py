from rest_framework import serializers
from usuarios.models import User
from polizas.models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, ReporteGenerado

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rol', 'is_active', 'first_name', 'last_name', 'telefono']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class AseguradoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aseguradora
        fields = '__all__'

class RamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ramo
        fields = '__all__'

class ContratanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contratante
        fields = '__all__'

class AseguradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asegurado
        fields = '__all__'

class PolizaSerializer(serializers.ModelSerializer):
    aseguradora = AseguradoraSerializer()
    ramo = RamoSerializer()
    forma_pago = serializers.StringRelatedField()
    contratante = ContratanteSerializer()
    asegurado = AseguradoSerializer()

    class Meta:
        model = Poliza
        fields = '__all__'

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = '__all__'