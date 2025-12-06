from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta, datetime
import openpyxl
from django.http import HttpResponse
from django.db.models import Q

# --- REMOVED: from apps.usuarios.models import User
from django.contrib.auth import get_user_model  # ADDED: Import get_user_model

# ADDED: Get the User model safely
User = get_user_model()

# Ensure FormaPago is imported here if it's used directly from models
from polizas.models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, ReporteGenerado, FormaPago

from .serializers import (
    UserSerializer,
    PolizaSerializer,
    AseguradoraSerializer,
    RamoSerializer,
    ContratanteSerializer,
    AseguradoSerializer,
    ReporteSerializer,
    CustomTokenObtainPairSerializer,
    FormaPagoSerializer
)


## Autenticación y Usuarios ##
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserLoginView(APIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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

    def patch(self, request):
        """Permite al usuario autenticado actualizar sus propios datos"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token es requerido"}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout exitoso."}, status=200)
        except Exception as e:
            return Response({"detail": f"Error logout: {str(e)}"}, status=400)


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
        'aseguradora', 'ramo', 'contratante', 'asegurado', 'forma_pago'
    ).all()
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['aseguradora', 'ramo', 'contratante', 'asegurado']

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(creado_por=self.request.user)
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Authentication required.")


class PolizaRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Poliza.objects.all()
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(actualizado_por=self.request.user)
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Authentication required.")


class PolizaProximaVencerList(generics.ListAPIView):
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['aseguradora', 'ramo', 'contratante']

    def get_queryset(self):
        fecha_str = self.request.query_params.get('fecha', None)
        if fecha_str:
            try:
                consult_date = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Formato de fecha inválido. Use YYYY-MM-DD.")
        else:
            consult_date = timezone.now().date()

        queryset = Poliza.objects.select_related(
            'aseguradora', 'ramo', 'contratante', 'asegurado', 'forma_pago'
        ).filter(
            renovacion__gte=consult_date
        ).order_by('renovacion')

        return queryset


class PolizaOptionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = {
            'aseguradoras': AseguradoraSerializer(Aseguradora.objects.all(), many=True).data,
            'ramos': RamoSerializer(Ramo.objects.all(), many=True).data,
            'contratantes': ContratanteSerializer(Contratante.objects.all(), many=True).data,
            'asegurados': AseguradoSerializer(Asegurado.objects.all(), many=True).data,
            'formas_pago': FormaPagoSerializer(FormaPago.objects.all(), many=True).data
        }
        return Response(data)


# Vistas para reportes
class GenerarReporteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReporteSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"status": "success", "reporte_id": 1})
        return Response(serializer.errors, status=400)


class ReporteHistorialList(generics.ListAPIView):
    serializer_class = ReporteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReporteGenerado.objects.filter(usuario=self.request.user)


# Vistas CRUD auxiliares (Aseguradoras, Ramos, etc)
class AseguradoraListCreateView(generics.ListCreateAPIView):
    queryset = Aseguradora.objects.all()
    serializer_class = AseguradoraSerializer
    permission_classes = [permissions.IsAuthenticated]


class AseguradoraRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Aseguradora.objects.all()
    serializer_class = AseguradoraSerializer
    permission_classes = [permissions.IsAuthenticated]


class RamoListCreateView(generics.ListCreateAPIView):
    queryset = Ramo.objects.all()
    serializer_class = RamoSerializer
    permission_classes = [permissions.IsAuthenticated]


class RamoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ramo.objects.all()
    serializer_class = RamoSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContratanteListCreateView(generics.ListCreateAPIView):
    queryset = Contratante.objects.all()
    serializer_class = ContratanteSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContratanteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contratante.objects.all()
    serializer_class = ContratanteSerializer
    permission_classes = [permissions.IsAuthenticated]


class AseguradoListCreateView(generics.ListCreateAPIView):
    queryset = Asegurado.objects.all()
    serializer_class = AseguradoSerializer
    permission_classes = [permissions.IsAuthenticated]


class AseguradoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asegurado.objects.all()
    serializer_class = AseguradoSerializer
    permission_classes = [permissions.IsAuthenticated]


class FormaPagoListCreateView(generics.ListCreateAPIView):
    queryset = FormaPago.objects.all()
    serializer_class = FormaPagoSerializer
    permission_classes = [permissions.IsAuthenticated]


class FormaPagoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FormaPago.objects.all()
    serializer_class = FormaPagoSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Vistas para el Módulo de Reportes ---

class PolizaReporteFilterMixin:
    def get_filtered_queryset(self):
        queryset = Poliza.objects.select_related(
            'aseguradora', 'ramo', 'contratante', 'asegurado', 'forma_pago'
        ).all()

        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        aseguradora_id = self.request.query_params.get('aseguradora')
        contratante_id = self.request.query_params.get('contratante')
        asegurado_id = self.request.query_params.get('asegurado')

        if fecha_desde and fecha_hasta:
            try:
                f_inicio = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                f_fin = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_inicio__range=[f_inicio, f_fin])
            except ValueError:
                pass

        if aseguradora_id:
            queryset = queryset.filter(aseguradora_id=aseguradora_id)
        if contratante_id:
            queryset = queryset.filter(contratante_id=contratante_id)
        if asegurado_id:
            queryset = queryset.filter(asegurado_id=asegurado_id)

        return queryset.order_by('fecha_inicio')


class PolizaReporteListView(generics.ListAPIView, PolizaReporteFilterMixin):
    serializer_class = PolizaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.get_filtered_queryset()


class ExportarPolizasExcelView(APIView, PolizaReporteFilterMixin):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = self.get_filtered_queryset()
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="reporte_polizas.xlsx"'

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Pólizas'

        columns = ['Nro Póliza', 'Aseguradora', 'Ramo', 'Forma Pago', 'Contratante', 'Asegurado', 'Fecha Inicio',
                   'Fecha Fin', 'Prima Total', 'Renovación']
        worksheet.append(columns)

        for poliza in queryset:
            worksheet.append([
                poliza.numero,
                poliza.aseguradora.nombre,
                poliza.ramo.nombre,
                poliza.forma_pago.nombre if poliza.forma_pago else '-',
                poliza.contratante.nombre,
                poliza.asegurado.nombre,
                poliza.fecha_inicio,
                poliza.fecha_fin,
                poliza.prima_total,
                poliza.renovacion
            ])

        workbook.save(response)
        return response


# --- NUEVA VISTA: Exportar Pólizas Próximas a Vencer ---
class ExportarPolizasProximasVencerExcelView(APIView):
    """
    Genera un Excel específicamente con las columnas que ve el Analista
    filtrado por fecha de renovación >= fecha consulta.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Filtro: misma lógica que PolizaProximaVencerList
        fecha_str = self.request.query_params.get('fecha', None)

        if fecha_str:
            try:
                consult_date = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return Response({"detail": "Fecha inválida"}, status=400)
        else:
            consult_date = timezone.now().date()

        queryset = Poliza.objects.select_related(
            'aseguradora', 'ramo', 'contratante', 'asegurado', 'forma_pago'
        ).filter(
            renovacion__gte=consult_date
        ).order_by('renovacion')

        # 2. Configurar Excel
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        filename = f"Proximas_Vencer_{consult_date}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = 'Próximas a Vencer'

        # 3. Columnas: Exactamente las que ve el Analista en su tabla
        columns = [
            'Aseguradora', 'Ramo', 'Forma Pago', 'Nro Póliza',
            'Contratante', 'Asegurado',
            'Vigencia',  # Combinamos inicio y fin como string
            'I Trimestre', 'II Trimestre', 'III Trimestre', 'IV Trimestre',
            'Prima Total', 'Renovación'
        ]
        worksheet.append(columns)

        # 4. Datos
        for poliza in queryset:
            # Manejo de nulos por seguridad
            aseg = poliza.aseguradora.nombre if poliza.aseguradora else '-'
            ramo = poliza.ramo.nombre if poliza.ramo else '-'
            pago = poliza.forma_pago.nombre if poliza.forma_pago else '-'
            cont = poliza.contratante.nombre if poliza.contratante else '-'
            aseg_pers = poliza.asegurado.nombre if poliza.asegurado else '-'

            # Formato de vigencia como string "YYYY-MM-DD - YYYY-MM-DD"
            vigencia_str = f"{poliza.fecha_inicio} - {poliza.fecha_fin}"

            worksheet.append([
                aseg, ramo, pago, poliza.numero,
                cont, aseg_pers,
                vigencia_str,
                poliza.i_trimestre, poliza.ii_trimestre,
                poliza.iii_trimestre, poliza.iv_trimestre,
                poliza.prima_total,
                poliza.renovacion
            ])

        workbook.save(response)
        return response