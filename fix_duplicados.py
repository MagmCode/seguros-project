import os
import django

# Ajusta 'seguros' al nombre real de tu carpeta de proyecto
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "seguros.settings")
django.setup()

# Importamos AMBOS modelos
from polizas.models import Contratante, Poliza


def eliminar_duplicados():
    target_doc = 'J-98765432-1'

    # 1. Identificar los contratantes duplicados
    contratantes_duplicados = Contratante.objects.filter(documento=target_doc)
    count = contratantes_duplicados.count()

    if count > 0:
        print(f"Encontrados {count} contratantes duplicados para {target_doc}.")

        # 2. Buscar las Pólizas asociadas a esos contratantes y borrarlas primero
        # Esto elimina el bloqueo del ProtectedError
        polizas_asociadas = Poliza.objects.filter(contratante__in=contratantes_duplicados)
        polizas_count = polizas_asociadas.count()

        if polizas_count > 0:
            print(f"Borrando {polizas_count} pólizas asociadas para liberar al contratante...")
            polizas_asociadas.delete()

        # 3. Ahora sí, borrar los contratantes
        print("Borrando contratantes...")
        contratantes_duplicados.delete()
        print("¡Limpieza completada con éxito!")

    else:
        print("No se encontraron duplicados.")


if __name__ == "__main__":
    eliminar_duplicados()