"""
Propósito: Define rutas para autenticación de usuarios (inicio de sesión, registro y verificación).
Funcionalidad: Proporciona endpoints /login, /register y /me para autenticar, registrar y 
obtener información del usuario autenticado usando JWT. Valida campos, hashea contraseñas con bcrypt 
y genera/verifica tokens JWT.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request  # Añade create_access_token
import mysql.connector
import bcrypt

# Crea el Blueprint para autenticación
auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    """
    Establece una conexión a la base de datos MySQL usando configuraciones de la app.
    
    Returns:
        mysql.connector.connection: Conexión a la base de datos.
    """
    return mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        database=current_app.config['MYSQL_DATABASE']
    )

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Requiere un token de refresco
def refresh():
    """
    Genera un nuevo token de acceso usando un token de refresco.
    
    Returns:
        JSON: Nuevo token de acceso o mensaje de error.
    """
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": access_token}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Inicia sesión de un usuario verificando número y contraseña, generando un token JWT.
    
    Request JSON:
        - numero (str): Identificador único del usuario.
        - contrasena (str): Contraseña del usuario.
    
    Returns:
        JSON: Token de acceso y datos del usuario o mensaje de error.
    """
    data = request.get_json()
    numero = data.get('numero')
    contrasena = data.get('contrasena')

    # Validación de campos
    if not all([numero, contrasena]):
        return jsonify({"error": "Número y contraseña son requeridos"}), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        # Busca el usuario por número
        cursor.execute("SELECT * FROM usuario WHERE numero = %s", (numero,))
        usuario = cursor.fetchone()
        
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Verifica la contraseña
        if bcrypt.checkpw(contrasena.encode('utf-8'), usuario['contrasena'].encode('utf-8')):
            access_token = create_access_token(identity=usuario['id'])
            refresh_token = create_refresh_token(identity=usuario['id'])  # Genera token de refresco
            return jsonify({
                "message": "Inicio de sesión exitoso",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "usuario": {
                    "id": usuario['id'],
                    "numero": usuario['numero'],
                    "nombre": usuario['nombre'],
                    "apellido": usuario['apellido']
                }
            }), 200
        else:
            return jsonify({"error": "Contraseña incorrecta"}), 401
    except mysql.connector.Error as err:
        return jsonify({"error": "Error al procesar el inicio de sesión"}), 500
    finally:
        cursor.close()
        connection.close()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Registra un nuevo usuario en la base de datos.
    
    Request JSON:
        - numero (str): Identificador único del usuario.
        - nombre (str): Nombre del usuario.
        - apellido (str): Apellido del usuario.
        - contrasena (str): Contraseña del usuario.
    
    Returns:
        JSON: Mensaje de éxito con datos del usuario creado o mensaje de error.
    """
    data = request.get_json()
    numero = data.get('numero')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    contrasena = data.get('contrasena')

    # Validación de campos
    if not all([numero, nombre, apellido, contrasena]):
        return jsonify({"error": "Número, nombre, apellido y contraseña son requeridos"}), 400
    
    # Validar longitud mínima de la contraseña
    if len(contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Verifica si el número ya está registrado
        cursor.execute("SELECT id FROM usuario WHERE numero = %s", (numero,))
        if cursor.fetchone():
            return jsonify({"error": "El número ya está registrado"}), 409

        # Hashea la contraseña
        hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

        # Inserta el nuevo usuario
        cursor.execute(
            "INSERT INTO usuario (numero, nombre, apellido, contrasena) VALUES (%s, %s, %s, %s)",
            (numero, nombre, apellido, hashed_password)
        )
        connection.commit()
        id = cursor.lastrowid

        # Genera un token JWT para el nuevo usuario
        access_token = create_access_token(identity=id)
        refresh_token = create_refresh_token(identity=id)  # Genera token de refresco
        return jsonify({
            "message": "Usuario registrado exitosamente",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "usuario": {
                "id": id,
                "numero": numero,
                "nombre": nombre,
                "apellido": apellido
            }
        }), 201
    except mysql.connector.Error as err:
        return jsonify({"error": "Error al registrar el usuario"}), 500
    finally:
        cursor.close()
        connection.close()

@auth_bp.route('/me', methods=['GET'])
@jwt_required()  # Protege esta ruta con JWT
def get_current_user():
    """
    Obtiene los datos del usuario autenticado basado en el token JWT.
    
    Returns:
        JSON: Datos del usuario o mensaje de error.
    """
    user_id = get_jwt_identity()  # Obtiene el ID del usuario desde el token
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, numero, nombre, apellido FROM usuario WHERE id = %s", (user_id,))
        usuario = cursor.fetchone()
        if usuario:
            return jsonify({
                "message": "Usuario encontrado",
                "usuario": usuario
            }), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except mysql.connector.Error as err:
        return jsonify({"error": "Error al obtener el usuario"}), 500
    finally:
        cursor.close()
        connection.close()