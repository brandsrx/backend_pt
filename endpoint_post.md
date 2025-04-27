# Social Media API (MongoDB)

Este documento describe la API para la funcionalidad de **posts**, **comentarios** y **likes** en una red social similar a Twitter, diseñada bajo el patrón **MVC** (Modelo-Vista-Controlador) y siguiendo estándares **RESTful**. La API utiliza **MongoDB** como base de datos NoSQL y devuelve respuestas en formato JSON. Requiere autenticación JWT para ciertas operaciones.

## Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Autenticación](#autenticación)
- [Endpoints](#endpoints)
  - [Posts](#posts)
  - [Comentarios](#comentarios)
  - [Likes](#likes)
- [Notas de Implementación](#notas-de-implementación)
- [Estructura MVC](#estructura-mvc)
- [Validaciones](#validaciones)
- [Base de Datos (MongoDB)](#base-de-datos-mongodb)

## Descripción General
La API permite a los usuarios:
- Crear, obtener y eliminar posts (máximo 280 caracteres, con soporte opcional para multimedia).
- Comentar en posts y obtener listas de comentarios.
- Dar y quitar likes a posts, así como consultar quién dio like.
Los endpoints están diseñados para ser escalables, con paginación en listas y validaciones robustas, aprovechando la flexibilidad de MongoDB para manejar documentos JSON.

## Autenticación
- Los endpoints que modifican datos (POST, DELETE) requieren un token JWT en el header:
  ```
  Authorization: Bearer <token>
  ```
- Los endpoints de lectura (GET) son opcionales para autenticación, pero pueden devolver datos personalizados si el usuario está autenticado.
- Implementar límites de tasa (e.g., 100 solicitudes/minuto por usuario) para prevenir abusos.

## Endpoints

### Posts
#### Crear un Post
- **Método**: POST
- **Ruta**: `/api/posts`
- **Descripción**: Crea un nuevo post.
- **Autenticación**: Requiere JWT.
- **Cuerpo de la solicitud**:
  ```json
  {
    "content": "¡Mi primer post!",
    "media_urls": ["https://example.com/image.jpg"],
    "parent_post_id": null
  }
  ```
- **Respuesta** (201 Created):
  ```json
  {
    "_id": "post_123",
    "user_id": "user_456",
    "content": "¡Mi primer post!",
    "media_urls": ["https://example.com/image.jpg"],
    "parent_post_id": null,
    "created_at": "2025-04-26T10:00:00Z",
    "likes_count": 0,
    "comments_count": 0
  }
  ```
- **Errores**:
  - 400: Contenido excede 280 caracteres.
  - 401: No autorizado.

#### Obtener un Post
- **Método**: GET
- **Ruta**: `/api/posts/:post_id`
- **Descripción**: Obtiene un post específico.
- **Autenticación**: Opcional.
- **Parámetros**: `post_id` (en la URL).
- **Respuesta** (200 OK):
  ```json
  {
    "_id": "post_123",
    "user_id": "user_456",
    "username": "juanperez",
    "content": "¡Mi primer post!",
    "media_urls": ["https://example.com/image.jpg"],
    "parent_post_id": null,
    "created_at": "2025-04-26T10:00:00Z",
    "likes_count": 10,
    "comments_count": 5
  }
  ```
- **Errores**:
  - 404: Post no encontrado.

#### Obtener Lista de Posts (Timeline)
- **Método**: GET
- **Ruta**: `/api/posts`
- **Descripción**: Obtiene una lista paginada de posts.
- **Autenticación**: Opcional.
- **Parámetros de consulta**:
  - `limit` (opcional, default: 20)
  - `skip` (opcional, default: 0, usado en lugar de `offset` para MongoDB)
  - `user_id` (opcional, filtra por usuario)
- **Respuesta** (200 OK):
  ```json
  {
    "posts": [
      {
        "_id": "post_123",
        "user_id": "user_456",
        "username": "juanperez",
        "content": "¡Mi primer post!",
        "media_urls": [],
        "parent_post_id": null,
        "created_at": "2025-04-26T10:00:00Z",
        "likes_count": 10,
        "comments_count": 5
      }
    ],
    "total": 1
  }
  ```

#### Eliminar un Post
- **Método**: DELETE
- **Ruta**: `/api/posts/:post_id`
- **Descripción**: Elimina un post (solo el dueño).
- **Autenticación**: Requiere JWT.
- **Parámetros**: `post_id` (en la URL).
- **Respuesta** (204 No Content): Sin cuerpo.
- **Errores**:
  - 403: No tienes permiso.
  - 404: Post no encontrado.

### Comentarios
#### Crear un Comentario
- **Método**: POST
- **Ruta**: `/api/posts/:post_id/comments`
- **Descripción**: Crea un comentario en un post.
- **Autenticación**: Requiere JWT.
- **Parámetros**: `post_id` (en la URL).
- **Cuerpo de la solicitud**:
  ```json
  {
    "content": "¡Gran post!"
  }
  ```
- **Respuesta** (201 Created):
  ```json
  {
    "_id": "comment_789",
    "post_id": "post_123",
    "user_id": "user_456",
    "content": "¡Gran post!",
    "created_at": "2025-04-26T10:05:00Z"
  }
  ```
- **Errores**:
  - 400: Contenido excede 280 caracteres.
  - 404: Post no encontrado.

#### Obtener Comentarios
- **Método**: GET
- **Ruta**: `/api/posts/:post_id/comments`
- **Descripción**: Obtiene una lista pag detached de comentarios.
- **Autenticación**: Opcional.
- **Parámetros**:
  - `post_id` (en la URL)
  - `limit` (opcional, default: 20)
  - `skip` (opcional, default: 0)
- **Respuesta** (200 OK):
  ```json
  {
    "comments": [
      {
        "_id": "comment_789",
        "post_id": "post_123",
        "user_id": "user_456",
        "username": "juanperez",
        "content": "¡Gran post!",
        "created_at": "2025-04-26T10:05:00Z"
      }
    ],
    "total": 1
  }
  ```

#### Eliminar un Comentario
- **Método**: DELETE
- **Ruta**: `/api/comments/:comment_id`
- **Descripción**: Elimina un comentario (solo el dueño).
- **Autenticación**: Requiere JWT.
- **Parámetros**: `comment_id` (en la URL).
- **Respuesta** (204 No Content): Sin cuerpo.
- **Errores**:
  - 403: No tienes permiso.
  - 404: Comentario no encontrado.

## Notas de Implementación
- **Paginación**: Usar `limit` y `skip` en endpoints GET para listas, compatible con MongoDB.
- **Rate Limiting**: Implementar límites de solicitudes para prevenir abusos (e.g., 100 solicitudes/minuto por usuario).
- **Errores**: Devolver códigos de estado HTTP apropiados (400, 401, 403, 404, etc.) con mensajes claros.
- **Caché**: Usar Redis o MongoDB TTL para endpoints GET con alta carga (e.g., timeline).
- **Índices**: Crear índices en MongoDB para optimizar consultas frecuentes (ver sección de Base de Datos).

## Estructura MVC
- **Modelos**:
  - `Post`: Maneja la lógica de MongoDB para posts (colección `posts`).
  - `Comment`: Maneja comentarios (colección `comments`).
- **Controladores**:
  - `PostController`: Maneja rutas y lógica de negocio para posts.
  - `CommentController`: Maneja comentarios.
- **Vistas**: Respuestas JSON serializadas.

## Validaciones
- Contenido de posts y comentarios: Máximo 280 caracteres.
- URLs de multimedia: Validar formato y tamaño (e.g., regex para URLs válidas).
- Recursos referenciados (e.g., `post_id`, `comment_id`): Verificar existencia en MongoDB antes de procesar.
- Unicidad: Usar índices únicos en MongoDB para evitar likes duplicados (en `post_id`, `user_id`).

## Base de Datos (MongoDB)

### Colecciones
#### Colección `posts`
- **Esquema**:
  ```javascript
  {
    _id: ObjectId, // o string (e.g., "post_123")
    user_id: String, // ID del usuario
    username: String, // Nombre del usuario (desnormalizado para consultas rápidas)
    content: String, // Máximo 280 caracteres
    media_urls: [String], // URLs de imágenes/videos (opcional)
    parent_post_id: String || null, // ID del post padre (para respuestas)
    created_at: Date, // Fecha de creación
    likes_count: Number, // Contador de likes
    comments_count: Number // Contador de comentarios
  }
  ```
- **Índices**:
  ```javascript
  db.posts.createIndex({ user_id: 1 });
  db.posts.createIndex({ parent_post_id: 1 });
  db.posts.createIndex({ created_at: -1 }); // Para ordenar timeline
  ```

#### Colección `comments`
- **Esquema**:
  ```javascript
  {
    _id: ObjectId, // o string (e.g., "comment_789")
    post_id: String, // ID del post asociado
    user_id: String, // ID del usuario
    username: String, // Nombre del usuario (desnormalizado)
    content: String, // Máximo 280 caracteres
    created_at: Date // Fecha de creación
  }
  ```
- **Índices**:
  ```javascript
  db.comments.createIndex({ post_id: 1 });
  db.comments.createIndex({ user_id: 1 });
  db.comments.createIndex({ created_at: -1 });
  ```


### Consideraciones para MongoDB
- **Desnormalización**: Almacenar `username` en `posts` y `comments` para evitar consultas adicionales al buscar información del usuario. Actualizar este campo si el usuario cambia su nombre (usar un evento o job).
- **Contadores**: Mantener `likes_count` y `comments_count` en la colección `posts` para consultas rápidas. Actualizarlos atómicamente con operaciones como `$inc`:
  ```javascript
  db.posts.updateOne(
    { _id: "post_123" },
    { $inc: { likes_count: 1 } }
  );
  ```
- **Paginación**: Usar `skip` y `limit` en consultas para paginación:
  ```javascript
  db.posts.find({}).sort({ created_at: -1 }).skip(0).limit(20);
  ```
- **Escalabilidad**: Considerar sharding en `posts` y `comments` por `user_id` o `created_at` para manejar grandes volúmenes de datos.
- **Validación de Esquema**: Usar MongoDB Schema Validation para asegurar que los documentos cumplan con las reglas (e.g., `content` máximo 280 caracteres):
  ```javascript
  db.createCollection("posts", {
    validator: {
      $jsonSchema: {
        bsonType: "object",
        required: ["user_id", "content", "created_at"],
        properties: {
          content: { bsonType: "string", maxLength: 280 },
          media_urls: { bsonType: "array", items: { bsonType: "string" } }
        }
      }
    }
  });
  ```