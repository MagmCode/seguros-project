# Seguros Project
Aplicación Django para gestión de seguros con API REST

## ⚙️ Requisitos Previos
- Python 3.10+
- PostgreSQL 12
- pip

## 🛠️ Configuración Inicial
### 1. Clonar el repositorio
 
```bash 
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
```

### 2. Crear y activar entorno virtual (venv)
```bash
# Crear entorno (Windows)
python -m venv venv
.\venv\Scripts\activate

# Crear entorno (Linux/Mac)
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
````bash
pip install -r requirements.txt
````


## 🐘 Configuración de PostgreSQL 12
### 1. Crear base de datos:
````sql
CREATE DATABASE nombre_db;
CREATE USER usuario_db WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE nombre_db TO usuario_db;
````
### 2. Configurar Django:
Editar settings.py con tus credenciales:

````python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nombre_db',
        'USER': 'usuario_db',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
````

### 3. Migrar la base de datos:

````bash
python manage.py migrate
````


## 🚦 Iniciar el Servidor de Desarrollo
Ejecutar en el puerto 8085:

````bash
python manage.py runserver 8085
Acceder: http://localhost:8085
````

## 📌 Comandos Útiles

| Comando                            | Descripcion                  |
|------------------------------------|------------------------------|
| `python manage.py createsuperuser` | Crear usuario admin          |
| `python manage.py makemigrations`  | Generar migraciones          |
| `python manage.py migrate`         | Migrar                       |
| `python manage.py collectstatic`   | Recopilar archivos estáticos |


## 🌐 Endpoints de la API
Lista los endpoints clave....