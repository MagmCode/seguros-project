from rest_framework import serializers
from usuarios.models import User
from polizas.models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, ReporteGenerado
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers

from polizas.models import FormaPago


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

class FormaPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPago
        fields = '__all__'


class PolizaSerializer(serializers.ModelSerializer):
    # Campos de lectura para mostrar el nombre en las respuestas GET.
    # Usamos `source` para mapearlos a los campos reales del modelo.
    aseguradora_nombre = AseguradoraSerializer(source='aseguradora', read_only=True)
    ramo_nombre = RamoSerializer(source='ramo', read_only=True)
    forma_pago_nombre = serializers.StringRelatedField(source='forma_pago', read_only=True)

    # Serializadores anidados para `contratante` y `asegurado`.
    # Estos permiten la escritura de objetos completos anidados en POST/PUT.
    contratante = ContratanteSerializer()
    asegurado = AseguradoSerializer()

    # Campos de escritura para las relaciones que se pasan por ID.
    # Son `write_only=True` para que no aparezcan en la respuesta GET.
    aseguradora_id = serializers.PrimaryKeyRelatedField(
        queryset=Aseguradora.objects.all(), source='aseguradora', write_only=True, required=True
    )
    ramo_id = serializers.PrimaryKeyRelatedField(
        queryset=Ramo.objects.all(), source='ramo', write_only=True, required=True
    )
    forma_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=FormaPago.objects.all(), source='forma_pago', write_only=True, required=True
    )

    class Meta:
        model = Poliza
        fields = [
            'id', 'numero', 'fecha_inicio', 'fecha_fin', 'renovacion',
            'i_trimestre', 'ii_trimestre', 'iii_trimestre', 'iv_trimestre',

            # Campos de escritura para IDs
            'aseguradora_id', 'ramo_id', 'forma_pago_id',

            # Campos de escritura anidados
            'contratante', 'asegurado',

            # Campos de lectura para nombres
            'aseguradora_nombre', 'ramo_nombre', 'forma_pago_nombre',
        ]

    def create(self, validated_data):
        # Extrae los datos de los objetos anidados
        contratante_data = validated_data.pop('contratante')
        asegurado_data = validated_data.pop('asegurado')

        # Crea o busca el Contratante y Asegurado por su campo 'documento'
        contratante, _ = Contratante.objects.get_or_create(
            documento=contratante_data.get('documento'),
            defaults=contratante_data
        )
        asegurado, _ = Asegurado.objects.get_or_create(
            documento=asegurado_data.get('documento'),
            defaults=asegurado_data
        )

        # Crea la póliza con las instancias de Contratante y Asegurado
        poliza = Poliza.objects.create(
            contratante=contratante,
            asegurado=asegurado,
            **validated_data
        )
        return poliza

    def update(self, instance, validated_data):
        # Maneja la actualización de campos anidados si se envían
        contratante_data = validated_data.pop('contratante', None)
        asegurado_data = validated_data.pop('asegurado', None)

        # Actualiza los campos de la póliza
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Actualiza los objetos Contratante y Asegurado si se enviaron datos
        if contratante_data:
            contratante_serializer = ContratanteSerializer(instance.contratante, data=contratante_data, partial=True)
            contratante_serializer.is_valid(raise_exception=True)
            contratante_serializer.save()

        if asegurado_data:
            asegurado_serializer = AseguradoSerializer(instance.asegurado, data=asegurado_data, partial=True)
            asegurado_serializer.is_valid(raise_exception=True)
            asegurado_serializer.save()

        instance.save()
        return instance

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = '__all__'