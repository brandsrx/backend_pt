from flask import Flask
from flask_jwt_extended import JWTManager
from config import Config
from database import init_db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.post_routes import post_bp
from routes.follow_routes import follow_bp

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

# Inicializar base de datos
init_db()

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(post_bp, url_prefix='/post')
app.register_blueprint(follow_bp, url_prefix='/follow')


if __name__ == "__main__":
    app.run(debug=True)