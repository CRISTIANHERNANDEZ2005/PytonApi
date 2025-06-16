"""
Propósito: Gestiona la configuración de la aplicación Flask.
Funcionalidad: Define clases de configuración para diferentes entornos (desarrollo, 
producción) que extraen variables de entorno desde .env. Proporciona una estructura 
centralizada para acceder a configuraciones como credenciales de MySQL y la clave secreta.
"""

import os
import secrets

class Config:
    """
    Configuración base para la aplicación.
    """
    # Configuración de la base de datos MySQL desde variables de entorno
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'tienda_online')

    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(16)) # Genera una clave segura de 32 caracteres
    print(SECRET_KEY)