from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

# --- REMOVED: from apps.usuarios.models import User
from django.contrib.auth import get_user_model # ADDED: Import get_user_model

# ADDED: Get the User model safely
User = get_user_model()

# Ensure FormaPago is imported here if it's used directly from models
from polizas.models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, ReporteGenerado, FormaPago # ADDED FormaPago

from .serializers import (
    UserSerializer,
    PolizaSerializer,
    AseguradoraSerializer,
    RamoSerializer,
    ContratanteSerializer,
    AseguradoSerializer,
    ReporteSerializer,
    CustomTokenObtainPairSerializer,
    FormaPagoSerializer # ADDED FormaPagoSerializer to imports
)


## Autenticación y Usuarios ##
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserLoginView(APIView):
    """
    Vista personalizada para login que incluye información adicional del usuario
    en la respuesta.
    """

    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # The CustomTokenObtainPairSerializer should expose the user via `serializer.user`
        # This line is technically correct if serializer.validated_data contains 'username'
        # and User.objects.get is used, but serializer.user is often more direct.
        # Keeping your original, it should work now that User is defined via get_user_model()
        user = User.objects.get(username=serializer.validated_data['username'])
        user_data = UserSerializer(user).data

        return Response({
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user': user_data
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Requiere autenticación

    def post(self, request):
        try:
            # Obtener el refresh token del body
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"detail": "Refresh token es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verificar y blacklist el refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"detail": "Logout exitoso. Token invalidado."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"detail": f"Error durante logout: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
# User Views
class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rol', 'is_active']


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


# Vistas para Pólizas
class PolizaListCreateView(generics.ListCreateAPIView):
    queryset = Poliza.objects.select_related(
        'aseguradora',
        'ramo',
        'contratante',
        'asegurado',
        'forma_pago'
    ).all()
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['aseguradora', 'ramo', 'contratante', 'asegurado']


class PolizaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Poliza.objects.all()
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated]


class PolizaProximaVencerList(generics.ListAPIView):
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['aseguradora', 'ramo', 'contratante']

    def get_queryset(self):
        fecha_consulta = self.request.query_params.get('fecha', None)

        if fecha_consulta:
            fecha_limite = timezone.datetime.strptime(fecha_consulta, '%Y-%m-%d').date()
        else:
            fecha_limite = timezone.now().date() + timedelta(days=30)

        return Poliza.objects.select_related(
            'aseguradora',
            'ramo',
            'contratante',
            'asegurado',
            'forma_pago'
        ).filter(
            fecha_fin__gte=timezone.now().date(),
            fecha_fin__lte=fecha_limite
        ).order_by('fecha_fin')


class PolizaOptionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = {
            'aseguradoras': AseguradoraSerializer(Aseguradora.objects.all(), many=True).data,
            'ramos': RamoSerializer(Ramo.objects.all(), many=True).data,
            'contratantes': ContratanteSerializer(Contratante.objects.all(), many=True).data,
            'asegurados': AseguradoSerializer(Asegurado.objects.all(), many=True).data,
            'formas_pago': FormaPagoSerializer(FormaPago.objects.all(), many=True).data # FIXED: Added FormaPagoSerializer
        }
        return Response(data)


# Vistas para reportes
class GenerarReporteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReporteSerializer(data=request.data)
        if serializer.is_valid():
            # CONSIDERATION: If ReporteGenerado.usuario is not nullable, you might need to
            # explicitly save the user here: serializer.save(usuario=request.user)
            # For now, keeping your original line.
            return Response({"status": "success", "reporte_id": 1}) # Check if you need to return actual ID
        return Response(serializer.errors, status=400)


class ReporteHistorialList(generics.ListAPIView):
    serializer_class = ReporteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReporteGenerado.objects.filter(usuario=self.request.user)



###################################################################
# Vistas para Aseguradoras
###################################################################
class AseguradoraListCreateView(generics.ListCreateAPIView):
    queryset = Aseguradora.objects.all()
    serializer_class = AseguradoraSerializer
    permission_classes = [permissions.IsAuthenticated]

class AseguradoraRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Aseguradora.objects.all()
    serializer_class = AseguradoraSerializer
    permission_classes = [permissions.IsAuthenticated]
####################################################################
# Vista para Ramo
####################################################################
class RamoListCreateView(generics.ListCreateAPIView):
    queryset = Ramo.objects.all()
    serializer_class = RamoSerializer
    permission_classes = [permissions.IsAuthenticated]

class RamoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ramo.objects.all()
    serializer_class = RamoSerializer
    permission_classes = [permissions.IsAuthenticated]
#####################################################################
#### Vistas para Contratante
#####################################################################
class ContratanteListCreateView(generics.ListCreateAPIView):
    queryset = Contratante.objects.all()
    serializer_class = ContratanteSerializer
    permission_classes = [permissions.IsAuthenticated]

class ContratanteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contratante.objects.all()
    serializer_class = ContratanteSerializer
    permission_classes = [permissions.IsAuthenticated]

#####################################################################
# Vistas para Asegurado
#####################################################################
class AseguradoListCreateView(generics.ListCreateAPIView):
    queryset = Asegurado.objects.all()
    serializer_class = AseguradoSerializer
    permission_classes = [permissions.IsAuthenticated]

class AseguradoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asegurado.objects.all()
    serializer_class = AseguradoSerializer
    permission_classes = [permissions.IsAuthenticated]

#####################################################################
# Vistas para Forma de Pago
#####################################################################
class FormaPagoListCreateView(generics.ListCreateAPIView):
    queryset = FormaPago.objects.all()
    serializer_class = FormaPagoSerializer
    permission_classes = [permissions.IsAuthenticated]

class FormaPagoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FormaPago.objects.all()
    serializer_class = FormaPagoSerializer
    permission_classes = [permissions.IsAuthenticated]