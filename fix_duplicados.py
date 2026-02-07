import os
import django

# CAMBIA 'seguros' POR EL NOMBRE DE TU CARPETA DE PROYECTO (donde está settings.py)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seguros.settings")
django.setup()

from polizas.models import Contratante  # Asegúrate que el modelo es Contratante


def eliminar_duplicados():
    target_doc = 'J-98765432-1'
    # Buscamos todos los registros con ese documento
    registros = Contratante.objects.filter(documento=target_doc)

    count = registros.count()
    if count > 1:
        print(f"Encontrados {count} registros duplicados para {target_doc}. Borrando...")
        # Borramos TODOS para asegurar que la tabla quede limpia y la migración pase.
        # Luego tu script 'create_test_users.py' lo volverá a crear limpio.
        registros.delete()
        print("Registros eliminados con éxito.")
    else:
        print("No se encontraron duplicados o el registro es único.")


if __name__ == "__main__":
    eliminar_duplicados()