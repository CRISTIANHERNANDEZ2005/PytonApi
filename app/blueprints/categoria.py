# Propósito: Contiene las rutas y lógica para las operaciones CRUD de la tabla categortia.
# Funcionalidad: Define un Blueprint (categoria_bp) que agrupa las rutas relacionadas con 
# categorías (por ejemplo, /categorias, /categorias/<id>). Incluye funciones para obtener todas las categorías, 
# obtener una categoría específica, crear, actualizar y eliminar categorías, con manejo de errores
# y conexión a la base de datos usando mysql.connector.


# Importa Blueprint, request, jsonify y current_app desde Flask
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required  # Importa jwt_required
# Importa mysql.connector para conectar con la base de datos
import mysql.connector

# Crea un Blueprint llamado 'categoria'
categoria_bp = Blueprint('categoria', __name__)

# Define una función para establecer la conexión con la base de datos
def get_db_connection():
    # Establece la conexión usando las configuraciones de current_app
    connection = mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],      # Host desde la configuración
        user=current_app.config['MYSQL_USER'],      # Usuario desde la configuración
        password=current_app.config['MYSQL_PASSWORD'],  # Contraseña desde la configuración
        database=current_app.config['MYSQL_DATABASE']  # Base de datos desde la configuración
    )
    return connection

# Ruta para obtener todas las categorías
@categoria_bp.route('/', methods=['GET'])
def get_categorias():
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor que devuelve resultados como diccionarios
    cursor = connection.cursor(dictionary=True)
    try:
        # Ejecuta la consulta para obtener todas las categorías
        cursor.execute("SELECT * FROM categortia")
        # Obtiene todos los resultados
        categorias = cursor.fetchall()
        # Devuelve las categorías en formato JSON
        return jsonify(categorias)
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al obtener categorías"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para obtener una categoría específica por ID
@categoria_bp.route('/<int:id>', methods=['GET'])
def get_categoria(id):
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor que devuelve resultados como diccionarios
    cursor = connection.cursor(dictionary=True)
    try:
        # Ejecuta la consulta para obtener la categoría por ID
        cursor.execute("SELECT * FROM categortia WHERE id = %s", (id,))
        # Obtiene el primer resultado
        categoria = cursor.fetchone()
        if categoria:
            # Si existe, devuelve la categoría en formato JSON
            return jsonify(categoria)
        else:
            # Si no existe, devuelve un error 404
            return jsonify({"error": "Categoría no encontrada"}), 404
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al obtener la categoría"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para crear una nueva categoría
@categoria_bp.route('/', methods=['POST'])
@jwt_required()  # Protege esta ruta
def create_categoria():
    # Obtiene los datos del cuerpo de la solicitud
    data = request.get_json()
    # Extrae el nombre de la categoría
    nombre = data.get('nombre')
    if not nombre:
        # Devuelve un error si falta el nombre
        return jsonify({"error": "El nombre es requerido"}), 400
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor
    cursor = connection.cursor()
    try:
        # Inserta la nueva categoría en la base de datos
        cursor.execute("INSERT INTO categortia (nombre) VALUES (%s)", (nombre,))
        # Confirma los cambios
        connection.commit()
        # Obtiene el ID de la nueva categoría
        id = cursor.lastrowid
        # Devuelve la categoría creada con código 201
        return jsonify("Categoría agregada",{"id": id, "nombre": nombre}), 201
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al crear la categoría"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para actualizar una categoría existente
@categoria_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()  # Protege esta ruta
def update_categoria(id):
    # Obtiene los datos del cuerpo de la solicitud
    data = request.get_json()
    # Extrae el nombre de la categoría
    nombre = data.get('nombre')
    if not nombre:
        # Devuelve un error si falta el nombre
        return jsonify({"error": "El nombre es requerido"}), 400
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor
    cursor = connection.cursor()
    try:
        # Actualiza la categoría en la base de datos
        cursor.execute("UPDATE categortia SET nombre = %s WHERE id = %s", (nombre, id))
        # Confirma los cambios
        connection.commit()
        if cursor.rowcount:
            # Si se actualizó, devuelve la categoría actualizada
            return jsonify("Categoría actualizada",{"id": id, "nombre": nombre})
        else:
            # Si no se encontró, devuelve un error 404
            return jsonify({"error": "Categoría no encontrada"}), 404
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al actualizar la categoría"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para eliminar una categoría
@categoria_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()  # Protege esta ruta
def delete_categoria(id):
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor
    cursor = connection.cursor()
    try:
        # Elimina la categoría de la base de datos
        cursor.execute("DELETE FROM categortia WHERE id = %s", (id,))
        # Confirma los cambios
        connection.commit()
        if cursor.rowcount:
            # Si se eliminó, devuelve un mensaje de éxito
            return jsonify({"message": "Categoría eliminada"})
        else:
            # Si no se encontró, devuelve un error 404
            return jsonify({"error": "Categoría no encontrada"}), 404
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al eliminar la categoría"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()