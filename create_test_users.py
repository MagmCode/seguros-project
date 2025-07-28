import os
import django
from django.core.management.color import no_style
from django.db import connection

# Configuración inicial
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seguros.settings')
django.setup()

from usuarios.models import User  # Asegúrate que esta importación coincida con tu modelo

def create_users():
    # Secuencia para resetear IDs (opcional, útil si recreas la DB frecuentemente)
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), [User])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)

    # Usuarios a crear (puedes añadir más)
    users_data = [
        {
            'username': '12345678',
            'first_name': 'Admin_Prueba',
            'last_name': 'Prueba',
            'email': 'admin@seguros.com',
            'password': 'Admin123*',
            'rol': 'admin',
            'is_superuser': True,
            'is_staff': True
        },
        {
            'username': '87654321',
            'first_name': 'Analista_Prueba',
            'last_name': 'Prueba',
            'email': 'analista@seguros.com',
            'password': 'Analista123*',
            'rol': 'analista',
            'is_superuser': False,
            'is_staff': True  # Acceso al admin pero sin permisos
        }
    ]

    for user_data in users_data:
        username = user_data['username']
        if not User.objects.filter(username=username).exists():
            try:
                if user_data['is_superuser']:
                    User.objects.create_superuser(**user_data)
                else:
                    User.objects.create_user(**user_data)
                print(f"✅ Usuario '{username}' creado exitosamente")
            except Exception as e:
                print(f"❌ Error creando '{username}': {str(e)}")
        else:
            print(f"⚠️ Usuario '{username}' ya existe, omitiendo creación")

if __name__ == '__main__':
    create_users()