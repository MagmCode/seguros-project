from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Autenticación
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Usuarios
    path('usuarios/', views.UserListCreateView.as_view(), name='user-list'),
    path('usuarios/<int:pk>/', views.UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),
    
    # Pólizas
    path('polizas/', views.PolizaListCreateView.as_view(), name='poliza-list'),
    path('polizas/<int:pk>/', views.PolizaRetrieveUpdateDestroyView.as_view(), name='poliza-detail'),
    path('polizas/proximas-vencer/', views.PolizaProximaVencerList.as_view(), name='poliza-proximas-vencer'),
    
    # Reportes
    path('reportes/generar/', views.GenerarReporteView.as_view(), name='generar-reporte'),
    path('reportes/historial/', views.ReporteHistorialList.as_view(), name='reporte-historial'),
]