# 🏪 Sistema de Mueblería - E-commerce Django

Un sistema completo de e-commerce para mueblería desarrollado en Django con funcionalidades avanzadas de gestión de productos, usuarios, blog, suscripciones y pagos.

## 🚀 Características Principales

### 🛍️ Gestión de Productos
- **Catálogo completo** con categorías y subcategorías
- **Sistema de búsqueda avanzada** con filtros por precio, categoría y características
- **Gestión de inventario** con control de stock
- **Galería de imágenes** con soporte para múltiples fotos por producto
- **Sistema de wishlist** para usuarios registrados
- **Exportación a Excel** de catálogos y reportes

### 👥 Gestión de Usuarios
- **Sistema de autenticación** completo (registro, login, logout)
- **Perfiles de usuario** personalizables
- **Sistema de roles** (admin, cliente, vendedor)
- **Gestión de direcciones** de envío
- **Historial de compras** y pedidos

### 📝 Blog y Contenido
- **Sistema de blog** integrado para artículos y noticias
- **Categorización** de contenido
- **Sistema de comentarios** en artículos
- **Editor de contenido** rico

### 💳 Sistema de Pagos
- **Integración con MercadoPago** para procesamiento de pagos
- **Múltiples métodos de pago** (tarjeta, transferencia, efectivo)
- **Gestión de suscripciones** y membresías
- **Sistema de facturación** automático

### 🎨 Interfaz de Usuario
- **Diseño responsive** optimizado para móviles y desktop
- **Tema moderno** con Bootstrap y CSS personalizado
- **Navegación intuitiva** con menús dinámicos
- **Carrito de compras** en tiempo real

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2.1** - Framework web principal
- **PostgreSQL** - Base de datos principal
- **Django REST Framework** - API REST
- **Python 3.13** - Lenguaje de programación

### Frontend
- **HTML5/CSS3** - Estructura y estilos
- **Bootstrap 5** - Framework CSS
- **JavaScript** - Interactividad
- **jQuery** - Manipulación DOM

### Servicios Externos
- **Azure Blob Storage** - Almacenamiento de archivos e imágenes
- **MercadoPago** - Procesamiento de pagos
- **Gmail SMTP** - Envío de correos electrónicos
- **Google Maps API** - Integración de mapas

### Producción
- **Azure App Service** - Hosting en la nube
- **Gunicorn** - Servidor WSGI de producción
- **Azure PostgreSQL** - Base de datos en la nube
- **SSL/TLS** - Seguridad de conexiones

## 📁 Estructura del Proyecto

```
muebleria/
├── muebleria/                 # Configuración principal del proyecto
│   ├── settings.py           # Configuraciones de Django
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # Configuración WSGI
│   ├── azure_storage.py     # Configuración Azure Blob Storage
│   └── custom_storage.py    # Backends de almacenamiento personalizados
├── login/                    # App de autenticación
├── productos/                # App de gestión de productos
│   ├── models.py            # Modelos de productos
│   ├── views.py             # Vistas de productos
│   ├── services/            # Servicios de negocio
│   └── admin.py             # Panel de administración
├── usuarios/                 # App de gestión de usuarios
├── blog/                    # App del blog
├── suscripciones/           # App de suscripciones
├── templates/               # Plantillas HTML
├── static/                  # Archivos estáticos (CSS, JS, imágenes)
├── media/                   # Archivos de medios (desarrollo local)
├── requirements.txt         # Dependencias del proyecto
└── .env                     # Variables de entorno (no incluido en repo)
```

## ⚙️ Instalación y Configuración

### Prerrequisitos
- Python 3.13+
- PostgreSQL 12+
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/muebleria.git
cd muebleria
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
# Django Security Settings
SECRET_KEY=tu_secret_key_aqui
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DBNAME=tu_base_de_datos
DBHOST=localhost
DBUSER=tu_usuario_postgres
DBPASS=tu_contraseña_postgres

# Azure Blob Storage (opcional para desarrollo)
USE_AZURE_STORAGE=False
AZURE_STORAGE_ACCOUNT_NAME=tu_cuenta_azure
AZURE_STORAGE_ACCOUNT_KEY=tu_clave_azure
AZURE_STORAGE_CONTAINER_NAME=media

# Email Configuration
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password

# Google API
GOOGLE_API_KEY=tu_google_api_key

# MercadoPago Configuration
PUBLIC_KEY=tu_mercadopago_public_key
ACCESS_TOKEN=tu_mercadopago_access_token
```

### 5. Configurar Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Cargar Datos de Prueba (Opcional)
```bash
python manage.py loaddata fixtures/datos_iniciales.json
```

### 7. Ejecutar Servidor de Desarrollo
```bash
python manage.py runserver
```

Visitar: http://127.0.0.1:8000

## 🚀 Despliegue en Azure

### 1. Configurar Azure App Service
- Crear App Service en Azure Portal
- Configurar Python 3.13 como runtime
- Habilitar HTTPS

### 2. Configurar Azure PostgreSQL
- Crear instancia de Azure Database for PostgreSQL
- Configurar firewall rules
- Obtener connection string

### 3. Configurar Azure Blob Storage
- Crear Storage Account en Azure
- Crear container para archivos
- Obtener access keys

### 4. Variables de Entorno en Azure
Configurar en Azure App Service → Configuration → Application settings:

```
SECRET_KEY=tu_secret_key_produccion
DEBUG=0
ALLOWED_HOSTS=tuapp.azurewebsites.net
CSRF_TRUSTED_ORIGINS=https://tuapp.azurewebsites.net
SECURE_SSL_REDIRECT=1
DBNAME=tu_base_datos_azure
DBHOST=tu_host_azure_postgres
DBUSER=tu_usuario_azure
DBPASS=tu_contraseña_azure
USE_AZURE_STORAGE=True
AZURE_STORAGE_ACCOUNT_NAME=tu_cuenta_azure
AZURE_STORAGE_ACCOUNT_KEY=tu_clave_azure
AZURE_STORAGE_CONTAINER_NAME=media
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
GOOGLE_API_KEY=tu_google_api_key
PUBLIC_KEY=tu_mercadopago_public_key
ACCESS_TOKEN=tu_mercadopago_access_token
```

### 5. Deploy desde GitHub
- Conectar Azure App Service con tu repositorio GitHub
- Configurar deployment source
- Ejecutar migraciones en producción

## 📊 Funcionalidades por Módulo

### 🛍️ Módulo de Productos
- **CRUD completo** de productos
- **Gestión de categorías** y subcategorías
- **Sistema de búsqueda** con filtros avanzados
- **Control de inventario** y stock
- **Galería de imágenes** múltiple
- **Exportación a Excel** de catálogos
- **Sistema de wishlist** para usuarios

### 👤 Módulo de Usuarios
- **Registro y autenticación** de usuarios
- **Perfiles personalizables** con avatar
- **Gestión de direcciones** múltiples
- **Historial de compras** detallado
- **Sistema de roles** y permisos
- **Recuperación de contraseña** por email

### 📝 Módulo de Blog
- **Gestión de artículos** y posts
- **Categorización** de contenido
- **Sistema de comentarios** moderado
- **Editor de contenido** rico
- **Búsqueda de contenido** por palabras clave
- **Sistema de tags** para organización

### 💳 Módulo de Suscripciones
- **Planes de suscripción** flexibles
- **Gestión de membresías** automática
- **Sistema de facturación** recurrente
- **Notificaciones** de vencimiento
- **Descuentos** por suscripción

## 🔧 Comandos Útiles

### Desarrollo
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar tests
python manage.py test
```

### Producción
```bash
# Ejecutar con Gunicorn
gunicorn muebleria.wsgi:application

# Recopilar archivos estáticos para producción
python manage.py collectstatic --noinput

# Ejecutar migraciones en producción
python manage.py migrate --noinput
```

## 🛡️ Seguridad

- **HTTPS** obligatorio en producción
- **CSRF protection** habilitado
- **XSS protection** configurado
- **SQL injection** prevenido con ORM
- **Autenticación segura** con Django
- **Variables de entorno** para datos sensibles
- **SSL/TLS** para conexiones de base de datos

## 📈 Rendimiento

- **Azure Blob Storage** para archivos estáticos
- **CDN** integrado con Azure
- **Caché** de consultas de base de datos
- **Compresión** de archivos estáticos
- **Optimización** de imágenes automática

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request


## 👨‍💻 Autor

**Fernando Flores Zaragoza**
- GitHub: [@Ferfloza3101](https://github.com/Ferfloza3101)
- Mail: ferfloza2003@gmail.com

