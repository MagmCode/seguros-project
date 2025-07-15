from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from usuarios.models import User
from polizas.models import Poliza, Aseguradora, Ramo, Contratante, Asegurado, ReporteGenerado
from .serializers import (
    UserSerializer,
    PolizaSerializer,
    AseguradoraSerializer,
    RamoSerializer,
    ContratanteSerializer,
    AseguradoSerializer,
    ReporteSerializer
)

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

class PolizaListCreateView(generics.ListCreateAPIView):
    queryset = Poliza.objects.all()
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
        
        return Poliza.objects.filter(
            fecha_fin__gte=timezone.now().date(),
            fecha_fin__lte=fecha_limite
        ).order_by('fecha_fin')

class GenerarReporteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Lógica para generar reporte
        serializer = ReporteSerializer(data=request.data)
        if serializer.is_valid():
            # Aquí iría la lógica para generar el reporte
            # Por ahora solo simulamos la respuesta
            return Response({"status": "success", "reporte_id": 1})
        return Response(serializer.errors, status=400)

class ReporteHistorialList(generics.ListAPIView):
    serializer_class = ReporteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReporteGenerado.objects.filter(usuario=self.request.user)