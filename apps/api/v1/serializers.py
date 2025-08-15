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
    aseguradora_nombre = AseguradoraSerializer(source='aseguradora', read_only=True)
    ramo_nombre = RamoSerializer(source='ramo', read_only=True)
    forma_pago_nombre = serializers.StringRelatedField(source='forma_pago', read_only=True)

    # Serializadores anidados para `contratante` y `asegurado`.
    contratante = ContratanteSerializer()
    asegurado = AseguradoSerializer()

    # Campos de escritura para las relaciones que se pasan por ID.
    aseguradora_id = serializers.PrimaryKeyRelatedField(
        queryset=Aseguradora.objects.all(), source='aseguradora', write_only=True, required=True
    )
    ramo_id = serializers.PrimaryKeyRelatedField(
        queryset=Ramo.objects.all(), source='ramo', write_only=True, required=True
    )
    # Forma de pago se usará para el cálculo, por eso es un campo de entrada.
    forma_pago_id = serializers.PrimaryKeyRelatedField(
        queryset=FormaPago.objects.all(), source='forma_pago', write_only=True, required=True
    )

    # Campos de trimestres como solo lectura (READ ONLY)
    i_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    ii_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    iii_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    iv_trimestre = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = Poliza
        fields = [
            'id', 'numero', 'fecha_inicio', 'fecha_fin', 'renovacion',

            # Los campos de trimestres son ahora de SÓLO LECTURA.
            'i_trimestre', 'ii_trimestre', 'iii_trimestre', 'iv_trimestre',

            # Campos de entrada de datos
            'prima_total',  'monto_asegurado',# <-- Campo para el monto total
            'aseguradora_id', 'ramo_id', 'forma_pago_id',
            'contratante', 'asegurado',

            # Campos de lectura para nombres
            'aseguradora_nombre', 'ramo_nombre', 'forma_pago_nombre',
        ]

    # --- MÉTODO PARA EL CÁLCULO DE PAGOS ---
    def _calculate_payments(self, poliza_instance, forma_pago_instance):
        forma_pago_name = forma_pago_instance.nombre.lower()
        prima_total = poliza_instance.prima_total

        if 'anual' in forma_pago_name:
            # Si es anual, divide el total entre 4
            monto_trimestre = prima_total / 4
            poliza_instance.i_trimestre = monto_trimestre
            poliza_instance.ii_trimestre = monto_trimestre
            poliza_instance.iii_trimestre = monto_trimestre
            poliza_instance.iv_trimestre = monto_trimestre
        elif 'semestral' in forma_pago_name:
            # Si es semestral, divide el total entre 2 y asigna a 1er y 2do trimestre
            monto_semestre = prima_total / 2
            poliza_instance.i_trimestre = monto_semestre
            poliza_instance.ii_trimestre = monto_semestre
            poliza_instance.iii_trimestre = 0
            poliza_instance.iv_trimestre = 0

        # Guardamos la póliza con los nuevos valores de trimestre
        poliza_instance.save()
        return poliza_instance

    # --- FIN DEL MÉTODO DE CÁLCULO ---

    def create(self, validated_data):
        contratante_data = validated_data.pop('contratante')
        asegurado_data = validated_data.pop('asegurado')
        forma_pago_instance = validated_data.pop('forma_pago')

        # 1. Obtenemos o creamos las instancias anidadas
        contratante, _ = Contratante.objects.get_or_create(
            documento=contratante_data.get('documento'),
            defaults=contratante_data
        )
        asegurado, _ = Asegurado.objects.get_or_create(
            documento=asegurado_data.get('documento'),
            defaults=asegurado_data
        )

        # 2. Creamos la instancia de la póliza SIN guardarla todavía
        poliza = Poliza(
            contratante=contratante,
            asegurado=asegurado,
            forma_pago=forma_pago_instance,
            **validated_data
        )

        # 3. Calculamos los pagos de los trimestres y los asignamos a la instancia
        poliza = self._calculate_payments(poliza, forma_pago_instance)

        # 4. Ahora sí, guardamos la instancia completa en la base de datos
        poliza.save()
        return poliza

    def update(self, instance, validated_data):
        # Maneja la actualización de campos anidados
        contratante_data = validated_data.pop('contratante', None)
        asegurado_data = validated_data.pop('asegurado', None)
        forma_pago_instance = validated_data.pop('forma_pago', instance.forma_pago)

        # Actualiza los campos de la póliza
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if contratante_data:
            contratante_serializer = ContratanteSerializer(instance.contratante, data=contratante_data, partial=True)
            contratante_serializer.is_valid(raise_exception=True)
            contratante_serializer.save()

        if asegurado_data:
            asegurado_serializer = AseguradoSerializer(instance.asegurado, data=asegurado_data, partial=True)
            asegurado_serializer.is_valid(raise_exception=True)
            asegurado_serializer.save()

        # Guarda los cambios de la póliza antes de calcular los trimestres
        instance.save()
        instance.forma_pago = forma_pago_instance  # Asigna la nueva forma de pago si existe

        # Recalcula los trimestres si la forma de pago o el monto total han cambiado
        if 'prima_total' in validated_data or 'forma_pago' in validated_data:
            return self._calculate_payments(instance, forma_pago_instance)

        return instance

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = '__all__'