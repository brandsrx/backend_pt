# API Backend SONET

**SONET** es el backend de una red social minimalista inspirada en Twitter, desarrollado en **Python** con el framework **Flask**.
Ofrece funcionalidades esenciales como registro y autenticación de usuarios, creación y gestión de publicaciones, seguimiento de usuarios, y mucho más, todo bajo una arquitectura modular, limpia y escalable.

---

## Tecnologías utilizadas

* **Python 3.13**
* **Flask** (Framework web ligero y rápido)
* **PyMongo** (Cliente para MongoDB)
* **Flask-JWT-Extended** (Gestión de autenticación mediante JWT)
* **redis** (Cliente de redis)

---

## Estructura del proyecto

```
backend_pt/
├── app/
│   ├── controllers/        # Rutas y lógica HTTP
│   ├── extensions/         # Extensiones y configuraciones externas
│   ├── middleware/         # Middlewares para procesamiento previo
│   ├── models/             # Definición de modelos de datos
│   ├── services/           # Lógica de negocio y servicios
│   ├── static/             # Archivos estáticos (imágenes, etc.)
│   ├── utils/              # Utilidades: compresión de imágenes, cache, etc.
│   ├── config.py           # Configuración general del proyecto
│   ├── database.py         # Conexión a MongoDB
│   └── run.py              # Punto de entrada principal de la API
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación del proyecto
```

---

## Instalación

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/brandsrx/backend_pt.git
   cd backend_pt
   ```

2. **Crear y activar un entorno virtual:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux / Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Configuración de MongoDB

1. Instala y ejecuta **MongoDB** localmente o utiliza un servicio en la nube como **MongoDB Atlas**.
2. Configura la URI de conexión en `app/config.py`:

   ```python
   MONGODB_URI = "mongodb://localhost:27017/social_network_db"
   ```

---

## Ejecutar la API

1. Exporta la variable de entorno `PYTHONPATH` para que la aplicación encuentre los módulos correctamente:

   ```powershell
   $env:PYTHONPATH = (Get-Location)  # Powershell en Windows
   $env:PYTHONPATH=pwd  # Powershell en Windows
   ```

   o en Linux/Mac:

   ```bash
   export PYTHONPATH=$(pwd)
   ```

2. Inicia la aplicación:

   ```bash
   python app/run.py
   ```

3. La API estará disponible en:

   ```
   http://127.0.0.1:5000/api
   ```

---

## Controlador de Autenticación (Auth)

Este módulo gestiona el registro, inicio y cierre de sesión de usuarios, integrando Redis para la revocación de tokens.

| Endpoint  | Método | Descripción                            | Autenticación | Parámetros / Body                                                                                                        | Respuesta destacada                           |
| --------- | ------ | -------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------- |
| `/signup` | POST   | Registro de nuevo usuario              | Ninguna       | `multipart/form-data`: `username`, `email`, `password` (obligatorios), `bio`, `is_private`, `profile_pic_url` (opcional) | `201`: Usuario registrado y token JWT emitido |
| `/login`  | POST   | Inicio de sesión                       | Ninguna       | JSON: `{ "username_or_email": str, "password": str }`                                                                    | `200`: Login exitoso con token JWT            |
| `/logout` | POST   | Cierre de sesión / revocación de token | JWT requerido | Ninguno                                                                                                                  | `200`: Token revocado correctamente           |

**Notas importantes:**

* `/signup` y `/login` no requieren autenticación previa.
* `/logout` requiere JWT válido y usa Redis para invalidar tokens.
* Se permite carga opcional de foto de perfil en `/signup`.
* Tokens JWT expiran en 24 horas e incluyen el nombre de usuario en sus claims.
* Se manejan errores con respuestas adecuadas y logging.

---

## Controlador de Usuarios (User)

Manejo de perfiles, privacidad, contraseña, búsqueda, seguimiento y recomendaciones.

| Endpoint               | Método | Descripción                  | Autenticación     | Parámetros / Body                                           | Respuesta destacada                                       |
| ---------------------- | ------ | ---------------------------- | ----------------- | ----------------------------------------------------------- | --------------------------------------------------------- |
| `/profile/picture`     | PUT    | Actualizar foto de perfil    | JWT requerido     | `multipart/form-data`: archivo imagen                       | `200`: Imagen actualizada correctamente                   |
| `/profile`             | PUT    | Actualizar campos del perfil | JWT requerido     | JSON con campos opcionales: `username`, `email`, `bio`      | `200`: Perfil actualizado                                 |
| `/privacy`             | PUT    | Configuración de privacidad  | JWT requerido     | JSON opcional: `is_private`, `show_email`, `allow_mentions` | `200`: Configuración de privacidad actualizada            |
| `/password`            | PUT    | Cambiar contraseña           | JWT requerido     | JSON: `current_password`, `new_password`                    | `200`: Contraseña cambiada correctamente                  |
| `/<username>`          | GET    | Ver perfil público           | Acceso opcional   | Path param: nombre de usuario                               | `200`: Perfil público o `404` si no existe                |
| `/<username>/follow`   | POST   | Seguir a usuario             | JWT requerido     | Path param: nombre de usuario                               | `200`: Confirmación de seguimiento                        |
| `/<username>/unfollow` | POST   | Dejar de seguir usuario      | JWT requerido     | Path param: nombre de usuario                               | `200`: Confirmación de dejar de seguir                    |
| `/search`              | GET    | Buscar usuarios por consulta | Sin autenticación | Query params: `q`, `limit` (default 20), `skip` (default 0) | `200`: Lista de usuarios coincidentes                     |
| `/recommend`           | GET    | Recomendaciones de usuarios  | JWT requerido     | Ninguno                                                     | `200`: Lista de usuarios recomendados (cacheada en Redis) |

**Notas importantes:**

* Endpoints protegidos usan `jwt_required()`.
* Cache en Redis para búsquedas y recomendaciones.
* Control de acceso a perfiles según privacidad.
* Gestión de subida de imagen para perfil.
* Manejo robusto de errores con logs.

---

## Endpoints del Controlador de Publicaciones

La siguiente tabla resume los endpoints proporcionados por el Blueprint `post`, que maneja la creación, recuperación, eliminación, me gusta, comentarios y gestión de feeds de publicaciones, integrado con la clase `FeedCache` para una distribución eficiente de feeds.

| Endpoint                            | Método  | Descripción                                      | Autenticación        | Cuerpo/Parámetros de la Solicitud                                                       | Respuesta                                                                 |
|-------------------------------------|---------|--------------------------------------------------|----------------------|---------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| `/`                                 | GET     | Recupera publicaciones (feed del usuario o global) | JWT opcional         | Consulta: `page` (entero, por defecto 1), `limit` (entero, por defecto 20)             | `200`: `{ "posts": [datos_publicacion], "total": entero }`<br>`404`: `{ "message": "No se encontraron publicaciones" }` |
| `/`                                 | POST    | Crea una nueva publicación con imágenes opcionales | JWT requerido        | `multipart/form-data`: `content` (str, opcional), `image` (lista de archivos, opcional) | `201`: `{ "message": "Publicación creada", "post_id": str }`<br>`400`: `{ "message": "Error al crear la publicación" }` |
| `/<post_id>`                        | GET     | Recupera una publicación específica por ID       | Ninguna              | Ruta: `post_id` (str)                                                                 | `200`: `{ "post": { "id": str, "content": str, "media_urls": [str], ... } }`<br>`404`: `{ "message": "Publicación no encontrada" }` |
| `/<post_id>`                        | DELETE  | Elimina una publicación (si el usuario es el autor) | JWT requerido        | Ruta: `post_id` (str)                                                                 | `200`: `{ "message": "Publicación eliminada" }`<br>`400`: `{ "message": "Error al eliminar la publicación" }`<br>`403`: `{ "message": "No autorizado" }` |
| `/feed`                             | GET     | Recupera el feed del usuario autenticado         | JWT requerido        | Consulta: `page` (entero, por defecto 1), `limit` (entero, por defecto 20)             | `200`: `{ "posts": [datos_publicacion], "total": entero }`<br>`404`: `{ "message": "No se encontraron publicaciones" }` |
| `/<post_id>/like`                   | POST    | Da me gusta a una publicación                    | JWT requerido        | Ruta: `post_id` (str)                                                                 | `200`: `{ "message": "Me gusta añadido" }`<br>`400`: `{ "message": "Error al dar me gusta" }`<br>`404`: `{ "message": "Publicación no encontrada" }` |
| `/<post_id>/dislike`                | POST    | Quita el me gusta de una publicación             | JWT requerido        | Ruta: `post_id` (str)                                                                 | `200`: `{ "message": "Me gusta eliminado" }`<br>`400`: `{ "message": "Error al quitar me gusta" }`<br>`404`: `{ "message": "Publicación no encontrada" }` |
| `/<post_id>/comment`                | POST    | Agrega un comentario a una publicación           | JWT requerido        | JSON: `{ "username": str, "profile_pic_url": str, "text_comment": str }`              | `200`: `{ "message": "Comentario añadido", "comment_id": str }`<br>`400`: `{ "message": "Error al añadir comentario" }`<br>`404`: `{ "message": "Publicación no encontrada" }` |
| `/<post_id>/comment`                | GET     | Recupera los comentarios de una publicación       | Ninguna              | Ruta: `post_id` (str)                                                                 | `200`: `{ "comments": [{ "id": str, "username": str, "text_comment": str, ... }] }`<br>`404`: `{ "message": "Publicación no encontrada" }` |
| `/<post_id>/comment/<comment_id>`   | DELETE  | Elimina un comentario de una publicación         | JWT requerido        | Ruta: `post_id` (str), `comment_id` (str)                                             | `200`: `{ "message": "Comentario eliminado" }`<br>`400`: `{ "message": "Error al eliminar comentario" }`<br>`404`: `{ "message": "Comentario no encontrado" }` |

### Notas
- **Autenticación**: La mayoría de los endpoints requieren JWT mediante `jwt_required()`, excepto `/` (GET) y `/<post_id>` (GET), donde el JWT es opcional o no es necesario.
- **Integración con Redis**: La clase `FeedCache` se utiliza en `/`, `/feed` y la creación de publicaciones para gestionar feeds de usuarios y globales, aprovechando el patrón de escritura de distribución (fanout write) para distribuir publicaciones a los feeds de los seguidores.
- **Limitación de Tasa**: Aplicada a `/` (GET) y `/<post_id>/like` con un límite de 100 solicitudes por 60 segundos.
- **Carga de Archivos**: El endpoint `/` (POST) soporta la carga de múltiples imágenes mediante `multipart/form-data`, procesadas por el servicio `UploadFile`.
- **Manejo de Errores**: Los endpoints devuelven códigos de estado apropiados (200, 201, 400, 403, 404) con mensajes JSON para éxito o errores.
- **Gestión de Feeds**: La función auxiliar `reload_feed_machine` asegura que el feed global esté poblado si está vacío, y `/feed` utiliza `FeedCache.get_feed_user` para feeds personalizados.

