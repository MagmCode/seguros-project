from rest_framework import serializers
from usuarios.models import User
from polizas.models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, ReporteGenerado
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['rol'] = user.rol
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra responses here
        user = User.objects.get(username=self.user.username)
        data['username'] = user.username
        data['email'] = user.email
        data['rol'] = user.rol
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name

        return data


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