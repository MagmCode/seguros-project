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

    # Pólizas
    path('polizas/', views.PolizaListCreateView.as_view(), name='poliza-list'),
    path('polizas/<int:pk>/', views.PolizaRetrieveUpdateDestroyView.as_view(), name='poliza-detail'),

    # --- PÓLIZAS PRÓXIMAS A VENCER ---
    path('polizas/proximas-vencer/', views.PolizaProximaVencerList.as_view(), name='poliza-proximas-vencer'),
    # NUEVO ENDPOINT PARA EXPORTAR
    path('polizas/proximas-vencer/exportar/', views.ExportarPolizasProximasVencerExcelView.as_view(),
         name='poliza-proximas-vencer-excel'),

    path('polizas/opciones/', views.PolizaOptionsView.as_view(), name='poliza-opciones'),

    # Reportes (Admin)
    path('reportes/generar/', views.GenerarReporteView.as_view(), name='generar-reporte'),
    path('reportes/historial/', views.ReporteHistorialList.as_view(), name='reporte-historial'),
    path('reportes/consulta/', views.PolizaReporteListView.as_view(), name='reporte-consulta'),
    path('reportes/exportar-excel/', views.ExportarPolizasExcelView.as_view(), name='reporte-excel'),

    # Auxiliares (Aseguradoras, Ramos, etc)
    path('aseguradoras/', views.AseguradoraListCreateView.as_view(), name='aseguradora-list'),
    path('aseguradoras/<int:pk>/', views.AseguradoraRetrieveUpdateDestroyView.as_view(), name='aseguradora-detail'),

    path('ramos/', views.RamoListCreateView.as_view(), name='ramo-list'),
    path('ramos/<int:pk>/', views.RamoRetrieveUpdateDestroyView.as_view(), name='ramo-detail'),

    path('contratantes/', views.ContratanteListCreateView.as_view(), name='contratante-list'),
    path('contratantes/<int:pk>/', views.ContratanteRetrieveUpdateDestroyView.as_view(), name='contratante-detail'),

    path('asegurados/', views.AseguradoListCreateView.as_view(), name='asegurado-list'),
    path('asegurados/<int:pk>/', views.AseguradoRetrieveUpdateDestroyView.as_view(), name='asegurado-detail'),

    path('formas-pago/', views.FormaPagoListCreateView.as_view(), name='formapago-list'),
    path('formas-pago/<int:pk>/', views.FormaPagoRetrieveUpdateDestroyView.as_view(), name='formapago-detail'),
]