# Cocina con Nosotros - Backend

## Descripción del Proyecto
Este proyecto consiste en un sistema de gestión de recetas de cocina, donde los usuarios pueden registrarse, autenticar su acceso, publicar recetas, agregar valoraciones, comentarios y realizar búsquedas avanzadas.

Cuenta con roles de usuario y moderador:
- **Usuarios**: Pueden visualizar, comentar y valorar recetas.
- **Moderadores**: Aprueban recetas y gestionan usuarios que incumplan las normas.

El sistema está implementado utilizando **Django** como framework backend y cumple con los requisitos de seguridad del Reglamento 128/2019 del MINCOM.

## Funcionalidades Principales
1. **Gestión de Usuarios**:
   - Registro y autenticación.
   - Inicio de sesión con usuario y contraseña.
   - Autenticación con Google mediante `django-allauth`.
   - Sistema de bloqueo tras intentos fallidos con `django-axes`.

2. **Publicación y Moderación de Recetas**:
   - Publicación de recetas con fotos, ingredientes y categorías (Desayunos, Comidas, Postres y Bebidas).
   - Moderación de recetas por parte de usuarios con rol de **moderador**.

3. **Interacción de Usuarios**:
   - Comentarios y valoraciones en recetas.
   - Búsquedas avanzadas y ordenamiento de recetas por fecha o categoría.

4. **Protección de Seguridad**:
   - Implementación de protección CSRF en formularios.
   - Validación estricta de contraseñas.
   - Acceso restringido a archivos privados mediante autenticación.

## Instalación y Configuración
Sigue estos pasos para configurar el proyecto:

1. Instala Python 3.11.
2. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   ```
3. Activa el entorno virtual:
   - En Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - En Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```
4. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
   Si alguna dependencia no se instala correctamente, hazlo manualmente.

5. Inicia el servidor:
   ```bash
   python manage.py runserver
   ```
   Para un servidor con SSL:
   ```bash
   python manage.py runsslserver
   ```
6. Accede desde tu navegador:
   - [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (HTTP)
   - [https://127.0.0.1:8000/](https://127.0.0.1:8000/) (HTTPS)

### **Credenciales de Administrador:**
- **Usuario**: `admin@example.com`
- **Contraseña**: `admin123`

## Requisitos de Seguridad Implementados
El proyecto cumple con los **requisitos del Reglamento 128/2019**:

1. **Autenticación de Usuario**:
   - Sistema de autenticación con usuario y contraseña.
   - OAuth para Google con `django-allauth`.
2. **Protección CSRF**:
   - Inclusión de `{% csrf_token %}` en formularios.
3. **Bloqueo de Usuarios**:
   - Uso de `django-axes` para bloquear usuarios tras intentos fallidos.
4. **Autorización y Control de Acceso**:
   - Restricción de recursos mediante `@login_required`.
   - Archivos privados protegidos mediante autenticación.
5. **Seguridad de Contraseñas**:
   - Validación estricta con configuraciones en `AUTH_PASSWORD_VALIDATORS`.
6. **Roles y Moderación**:
   - Moderadores pueden aprobar recetas y gestionar usuarios.
7. **Archivos Protegidos**:
   - Acceso controlado a medios y archivos estáticos.

## Dependencias
- **Django**
- **django-allauth** (OAuth)
- **django-axes** (bloqueo de usuarios)
- **DataTable JS**, **SweetAlert2**, **iziToast**, **Bootstrap** y **jQuery** (Frontend).

## Autores
- **Kevin Patterson** - [@KevPatterson](https://github.com/KevPatterson)
- **Diosmany Cereste** - [@EncriptorX](https://github.com/EncriptorX) 

---
© 2024 Cocina con Nosotros. Todos los derechos reservados.
