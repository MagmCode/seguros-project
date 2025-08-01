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
    # These fields are for READ-ONLY output (GET requests).
    # They will display the full nested object.
    aseguradora = AseguradoraSerializer(read_only=True)
    ramo = RamoSerializer(read_only=True)
    contratante = ContratanteSerializer
    asegurado = AseguradoSerializer
    forma_pago = serializers.StringRelatedField(read_only=True) # This shows the string name of FormaPago

    # These new fields are for WRITE-ONLY input (POST/PUT/PATCH requests).
    # They will accept the integer ID of the related object.
    aseguradora_id = serializers.PrimaryKeyRelatedField(
        queryset=Aseguradora.objects.all(), source='aseguradora', write_only=True
    )
    ramo_id = serializers.PrimaryKeyRelatedField(
        queryset=Ramo.objects.all(), source='ramo', write_only=True
    )
    contratante_id = serializers.PrimaryKeyRelatedField(
        queryset=Contratante.objects.all(), source='contratante', write_only=True
    )
    asegurado_id = serializers.PrimaryKeyRelatedField(
        queryset=Asegurado.objects.all(), source='asegurado', write_only=True
    )
    forma_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=FormaPago.objects.all(), source='forma_pago', write_only=True
    )

    class Meta:
        model = Poliza
        fields = [
            'id', # Always good to include
            'fecha_inicio', 'fecha_fin',
            # Include these for output (GET requests)
            'aseguradora', 'ramo', 'contratante', 'asegurado', 'forma_pago',
            # Include these for input (POST/PUT/PATCH requests)
            'aseguradora_id', 'ramo_id', 'contratante_id', 'asegurado_id', 'forma_pago_id',
            # These are the new required fields from your model
            'numero', 'vigencia', 'i_trimestre', 'ii_trimestre', 'iii_trimestre',
            'iv_trimestre', 'renovacion',

        ]

    def create(self, validated_data):
        # Extract nested data for contratante and asegurado
        contratante_data = validated_data.pop('contratante')
        asegurado_data = validated_data.pop('asegurado')

        # Get existing or create new Contratante/Asegurado based on unique fields (e.g., 'documento')
        # You need to decide your strategy here: always create new, or find existing?
        # For simplicity, let's assume always create new if unique fields are provided,
        # or find if they match an exact set of data.
        # A common approach is to use get_or_create on a unique field like 'documento'.

        # Example using 'documento' as the unique identifier for Contratante/Asegurado
        # Make sure 'documento' is required in ContratanteSerializer and AseguradoSerializer
        contratante, created_c = Contratante.objects.get_or_create(
            documento=contratante_data['documento'],
            defaults=contratante_data # Use all data if creating
        )
        if not created_c:
            # If not created, it means it already existed.
            # You might want to update its other fields here if the incoming data is newer/different
            for attr, value in contratante_data.items():
                setattr(contratante, attr, value)
            contratante.save()

        asegurado, created_a = Asegurado.objects.get_or_create(
            documento=asegurado_data['documento'],
            defaults=asegurado_data
        )
        if not created_a:
            for attr, value in asegurado_data.items():
                setattr(asegurado, attr, value)
            asegurado.save()

        # Assign the Contratante and Asegurado instances to the Poliza
        poliza = Poliza.objects.create(
            contratante=contratante,
            asegurado=asegurado,
            **validated_data
        )
        return poliza

    def update(self, instance, validated_data):
        # Handle nested updates for contratante and asegurado if they are in validated_data
        contratante_data = validated_data.pop('contratante', None)
        asegurado_data = validated_data.pop('asegurado', None)

        # Update parent fields first
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if contratante_data:
            # You might want to get_or_create here too, or simply update the existing
            # linked contratante. For a simple update, assuming you update the
            # currently linked contratante:
            contratante = instance.contratante
            for attr, value in contratante_data.items():
                setattr(contratante, attr, value)
            contratante.save()

        if asegurado_data:
            asegurado = instance.asegurado
            for attr, value in asegurado_data.items():
                setattr(asegurado, attr, value)
            asegurado.save()

        instance.save()
        return instance


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = '__all__'