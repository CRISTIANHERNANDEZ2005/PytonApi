"""
Propósito: Inicializa la aplicación Flask y configura sus componentes principales.
Funcionalidad: Define la función create_app() que crea la instancia de Flask, carga 
configuraciones desde .env a través de config.py, inicializa extensiones como CORS y JWT, 
configura la clave secreta y registra los Blueprints de categorías, productos, 
documentación y autenticación.
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # Importa JWTManager
from dotenv import load_dotenv
import os

from .config import Config
from .blueprints.categoria import categoria_bp
from .blueprints.producto import producto_bp
from .blueprints.documentacion import documentacion_bp
from .blueprints.auth import auth_bp

cors = CORS()
jwt = JWTManager()  # Instancia global de JWTManager

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configura la clave secreta para JWT (puedes usar la misma de .env o una específica)
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'Yeicy') 
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Los tokens se enviarán en los headers
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # Token de refresco expira en 7 días

    # Configura la clave secreta de la aplicación
    app.secret_key = app.config['SECRET_KEY']

    # Inicializa extensiones
    cors.init_app(app)
    jwt.init_app(app)  # Inicializa JWTManager

    # Registra Blueprints
    app.register_blueprint(categoria_bp, url_prefix='/categorias')
    app.register_blueprint(producto_bp, url_prefix='/productos')
    app.register_blueprint(documentacion_bp, url_prefix='/documentacion')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app