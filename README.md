# 🐦 Pytweet - Backend API

**Pytweet** es un backend para una red social minimalista inspirada en Twitter, desarrollado en **Python** con **Flask**.  
Soporta funcionalidades clave como registro de usuarios, autenticación, creación de publicaciones, y más, con una arquitectura modular y escalable.

---

## 🚀 Tecnologías utilizadas

- **Python 3.13** 🐍
- **Flask** 🌐 (Framework web ligero)
- **PyMongo** 🍃 (Integración con MongoDB)
- **Flask-JWT-Extended** 🔒 (Autenticación basada en JWT)
- **Flask-Smorest** 📜 (Documentación automática OpenAPI/Swagger)
- **Pytest** 🧪 (Pruebas automatizadas)

---

## 📂 Estructura del proyecto

```
backend_pt/
├── app/
│   ├── controllers/        # Rutas y lógica HTTP
│   ├── models/             # Modelos de datos
│   ├── services/           # Lógica de negocio
│   ├── tests/              # Pruebas automatizadas (Pytest)
│   │   ├── conftest.py     # Configuración de fixtures
│   │   └── test_auth_controller.py
│   ├── config.py           # Configuración de la aplicación
│   └── run.py              # Punto de entrada de la API
├── migrations/             # Scripts de migración (opcional)
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación del proyecto
```
---

## ⚙️ Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/brandsrx/backend_pt.git
   cd pytweet-backend
   ```

2. **Crea un entorno virtual**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Configuración de MongoDB

1. Asegúrate de tener **MongoDB** instalado y corriendo localmente o usa un servicio en la nube como **MongoDB Atlas**.
2. Configura la URI de conexión en `app/config.py`:
   ```python
   MONGODB_URI = "mongodb://localhost:27017/pytweet"
   ```

---

## ▶️ Ejecutar la API

1. Inicia la aplicación:
   ```bash
   python app/run.py
   ```

2. La API estará disponible en:
   ```
   http://127.0.0.1:5000/
   ```
---

## 🌐 Endpoints principales

| Método | Endpoint               | Descripción                       |
|--------|------------------------|-----------------------------------|
| POST   | `/api/auth/register`        | Registrar un nuevo usuario        |
| POST   | `/api/auth/login`           | Iniciar sesión (retorna JWT)      |
| POST   | `/api/posts`           | Crear un nuevo post               |
| GET    | `/api/posts`           | Listar todos los posts            |
| GET    | `/api/posts/<id>`      | Obtener un post específico        |

---

## 🧪 Ejecutar tests
### Antes de ejecutar los tests
- Windows:
``` bash
$env:PYTHONPATH="<la ruta de tu proyecto>"
```
- Linux:
```bash
export PYTHONPATH=$(pwd)
```
1. Asegúrate de tener las dependencias de desarrollo instaladas:
   ```bash
   pip install pytest
   ```

2. Ejecuta los tests:
   ```bash
   pytest app/tests/
   ```

---

## 🤝 Contribución

¡Contribuciones ! Sigue estos pasos:

1. Haz un **fork** del repositorio.
2. Crea una rama para tu feature:
   ```bash
   git checkout -b mi-nueva-feature
   ```
3. Realiza tus cambios y haz commit:
   ```bash
   git commit -m "Añade mi nueva feature"
   ```
4. Envía los cambios al repositorio remoto:
   ```bash
   git push origin mi-nueva-feature
   ```
5. Crea un **Pull Request** en GitHub.

---