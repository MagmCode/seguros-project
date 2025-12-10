from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Importa tus modelos
from polizas.models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, FormaPago, ReporteGenerado

User = get_user_model()


# ... (CustomTokenObtainPairSerializer y UserSerializer se mantienen IGUAL) ...

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['rol'] = user.rol
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['email'] = self.user.email
        data['rol'] = self.user.rol
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'rol', 'is_active', 'first_name', 'last_name', 'telefono']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'email': {'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if validated_data.get('rol') == 'admin':
            validated_data['is_staff'] = True
        else:
            validated_data['is_staff'] = False
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if 'rol' in validated_data:
            if validated_data['rol'] == 'admin':
                instance.is_staff = True
            else:
                instance.is_staff = False
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# --- Serializadores Auxiliares (Se mantienen IGUAL) ---

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


# --- SERIALIZADOR PRINCIPAL DE PÓLIZA (MODIFICADO) ---
class PolizaSerializer(serializers.ModelSerializer):
    aseguradora_nombre = AseguradoraSerializer(source='aseguradora', read_only=True)
    ramo_nombre = RamoSerializer(source='ramo', read_only=True)
    forma_pago_nombre = serializers.StringRelatedField(source='forma_pago', read_only=True)

    contratante = ContratanteSerializer()
    asegurado = AseguradoSerializer()

    aseguradora_id = serializers.PrimaryKeyRelatedField(
        queryset=Aseguradora.objects.all(), source='aseguradora', write_only=True, required=True
    )
    ramo_id = serializers.PrimaryKeyRelatedField(
        queryset=Ramo.objects.all(), source='ramo', write_only=True, required=True
    )
    forma_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=FormaPago.objects.all(), source='forma_pago', write_only=True, required=True
    )

    i_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    ii_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    iii_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    iv_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Poliza
        fields = [
            'id', 'numero', 'fecha_inicio', 'fecha_fin', 'renovacion',
            'i_trimestre', 'ii_trimestre', 'iii_trimestre', 'iv_trimestre',
            'prima_total', 'monto_asegurado',  # Aseguramos que monto_asegurado esté en fields
            'aseguradora_id', 'ramo_id', 'forma_pago_id',
            'contratante', 'asegurado',
            'aseguradora_nombre', 'ramo_nombre', 'forma_pago_nombre',
        ]

    def _calculate_payments(self, poliza_instance, forma_pago_instance):
        forma_pago_name = forma_pago_instance.nombre.lower()
        prima_total = float(poliza_instance.prima_total)

        if 'semestral' in forma_pago_name:
            monto_cuota = prima_total / 2
            poliza_instance.i_trimestre = monto_cuota
            poliza_instance.ii_trimestre = 0
            poliza_instance.iii_trimestre = monto_cuota
            poliza_instance.iv_trimestre = 0
        else:
            monto_cuota = prima_total / 4
            poliza_instance.i_trimestre = monto_cuota
            poliza_instance.ii_trimestre = monto_cuota
            poliza_instance.iii_trimestre = monto_cuota
            poliza_instance.iv_trimestre = monto_cuota

        return poliza_instance

    def create(self, validated_data):
        contratante_data = validated_data.pop('contratante')
        asegurado_data = validated_data.pop('asegurado')
        forma_pago_instance = validated_data.pop('forma_pago')

        # Manejo robusto de Contratante/Asegurado
        contratante_qs = Contratante.objects.filter(documento=contratante_data.get('documento'))
        contratante = contratante_qs.first() if contratante_qs.exists() else Contratante.objects.create(
            **contratante_data)

        asegurado_qs = Asegurado.objects.filter(documento=asegurado_data.get('documento'))
        asegurado = asegurado_qs.first() if asegurado_qs.exists() else Asegurado.objects.create(**asegurado_data)

        # 1. Creamos la instancia Poliza
        poliza = Poliza(
            contratante=contratante,
            asegurado=asegurado,
            forma_pago=forma_pago_instance,
            # 2. AÑADIMOS TODOS LOS CAMPOS RESTANTES A LA INSTANCIA ANTES DE CALCULAR/GUARDAR
            **validated_data
        )

        # 3. Calculamos trimestres
        poliza = self._calculate_payments(poliza, forma_pago_instance)

        # 4. Guardamos
        poliza.save()
        return poliza

    def update(self, instance, validated_data):
        # ... (La lógica de update se mantiene igual)
        contratante_data = validated_data.pop('contratante', None)
        asegurado_data = validated_data.pop('asegurado', None)
        forma_pago_instance = validated_data.pop('forma_pago', instance.forma_pago)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if contratante_data:
            contratante_serializer = ContratanteSerializer(instance.contratante, data=contratante_data, partial=True)
            if contratante_serializer.is_valid(raise_exception=True):
                contratante_serializer.save()

        if asegurado_data:
            asegurado_serializer = AseguradoSerializer(instance.asegurado, data=asegurado_data, partial=True)
            if asegurado_serializer.is_valid(raise_exception=True):
                asegurado_serializer.save()

        if 'prima_total' in validated_data or 'forma_pago' in validated_data:
            instance.forma_pago = forma_pago_instance
            instance = self._calculate_payments(instance, forma_pago_instance)

        instance.save()
        return instance


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = '__all__'