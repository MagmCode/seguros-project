from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    # Autenticación JWT
    path('auth/login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='logout'),

    # Perfil de usuario
    path('usuarios/perfil/', views.UserProfileView.as_view(), name='user-profile'),

    # Usuarios
    path('usuarios/', views.UserListCreateView.as_view(), name='user-list'),
    path('usuarios/<int:pk>/', views.UserRetrieveUpdateDestroyView.as_view(), name='user-detail'),

    # Pólizas (mantén tus rutas existentes)
    path('polizas/', views.PolizaListCreateView.as_view(), name='poliza-list'),
    path('polizas/<int:pk>/', views.PolizaRetrieveUpdateDestroyView.as_view(), name='poliza-detail'),
    path('polizas/proximas-vencer/', views.PolizaProximaVencerList.as_view(), name='poliza-proximas-vencer'),

    # Reportes
    path('reportes/generar/', views.GenerarReporteView.as_view(), name='generar-reporte'),
    path('reportes/historial/', views.ReporteHistorialList.as_view(), name='reporte-historial'),
]