# Propósito: Contiene las rutas y lógica para las operaciones CRUD de la tabla producto.
# Funcionalidad: Define un Blueprint (producto_bp) que agrupa las rutas relacionadas 
# con productos (por ejemplo, /productos, /productos/<id>). Incluye funciones para obtener todos los productos, 
# obtener un producto específico, crear, actualizar y eliminar productos, con validaciones 
# como verificar la existencia de categorías y manejo de errores.


# Importa Blueprint, request, jsonify y current_app desde Flask
from flask import Blueprint, request, jsonify, current_app
# Importa mysql.connector para conectar con la base de datos
from flask_jwt_extended import jwt_required  # Importa jwt_required
import mysql.connector

# Crea un Blueprint llamado 'producto'
producto_bp = Blueprint('producto', __name__)

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

# Ruta para obtener todos los productos
@producto_bp.route('/', methods=['GET'])
def get_productos():
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor que devuelve resultados como diccionarios
    cursor = connection.cursor(dictionary=True)
    try:
        # Ejecuta la consulta para obtener todos los productos
        cursor.execute("SELECT * FROM producto")
        # Obtiene todos los resultados
        productos = cursor.fetchall()
        # Devuelve los productos en formato JSON
        return jsonify(productos)
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al obtener los productos"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para obtener un producto específico por ID
@producto_bp.route('/<int:id>', methods=['GET'])
def get_producto(id):
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor que devuelve resultados como diccionarios
    cursor = connection.cursor(dictionary=True)
    try:
        # Ejecuta la consulta para obtener el producto por ID
        cursor.execute("SELECT * FROM producto WHERE id = %s", (id,))
        # Obtiene el primer resultado
        producto = cursor.fetchone()
        if producto:
            # Si existe, devuelve el producto en formato JSON
            return jsonify(producto)
        else:
            # Si no existe, devuelve un error 404
            return jsonify({"error": "Producto no encontrado"}), 404
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al obtener el producto"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para crear un nuevo producto
@producto_bp.route('/', methods=['POST'])
@jwt_required()  # Protege esta ruta
def create_producto():
    # Obtiene los datos del cuerpo de la solicitud
    data = request.get_json()
    # Extrae los campos necesarios
    nombre = data.get('nombre')
    precio = data.get('precio')
    descripcion = data.get('descripcion')
    categortia_id = data.get('categortia_id')
    if not all([nombre, precio, categortia_id]):
        # Devuelve un error si faltan campos requeridos
        return jsonify({"error": "Nombre, precio y categortia_id son requeridos"}), 400
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor
    cursor = connection.cursor()
    try:
        # Verifica si la categoría existe
        cursor.execute("SELECT id FROM categortia WHERE id = %s", (categortia_id,))
        if not cursor.fetchone():
            # Devuelve un error si la categoría no existe
            return jsonify({"error": "Categoría no encontrada"}), 404
        # Inserta el nuevo producto en la base de datos
        cursor.execute(
            "INSERT INTO producto (nombre, precio, descripcion, categortia_id) VALUES (%s, %s, %s, %s)",
            (nombre, precio, descripcion, categortia_id)
        )
        # Confirma los cambios
        connection.commit()
        # Obtiene el ID del nuevo producto
        id = cursor.lastrowid
        # Devuelve el producto creado con código 201
        return jsonify("Producto agregado",{"id": id, "nombre": nombre, "precio": precio, "descripcion": descripcion, "categortia_id": categortia_id}), 201
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al crear el producto"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para actualizar un producto existente
@producto_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()  # Protege esta ruta
def update_producto(id):
    # Obtiene los datos del cuerpo de la solicitud
    data = request.get_json()
    # Extrae los campos necesarios
    nombre = data.get('nombre')
    precio = data.get('precio')
    descripcion = data.get('descripcion')
    categortia_id = data.get('categortia_id')
    if not all([nombre, precio, categortia_id]):
        # Devuelve un error si faltan campos requeridos
        return jsonify({"error": "Nombre, precio y categortia_id son requeridos"}), 400
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor
    cursor = connection.cursor()
    try:
        # Verifica si la categoría existe
        cursor.execute("SELECT id FROM categortia WHERE id = %s", (categortia_id,))
        if not cursor.fetchone():
            # Devuelve un error si la categoría no existe
            return jsonify({"error": "Categoría no encontrada"}), 404
        # Actualiza el producto en la base de datos
        cursor.execute(
            "UPDATE producto SET nombre = %s, precio = %s, descripcion = %s, categortia_id = %s WHERE id = %s",
            (nombre, precio, descripcion, categortia_id, id)
        )
        # Confirma los cambios
        connection.commit()
        if cursor.rowcount:
            # Si se actualizó, devuelve el producto actualizado
            return jsonify("Producto actualizado",{"id": id, "nombre": nombre, "precio": precio, "descripcion": descripcion, "categortia_id": categortia_id})
        else:
            # Si no se encontró, devuelve un error 404
            return jsonify({"error": "Producto no encontrado"}), 404
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al actualizar el producto"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()

# Ruta para eliminar un producto
@producto_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()  # Protege esta ruta
def delete_producto(id):
    # Establece la conexión con la base de datos
    connection = get_db_connection()
    # Crea un cursor
    cursor = connection.cursor()
    try:
        # Elimina el producto de la base de datos
        cursor.execute("DELETE FROM producto WHERE id = %s", (id,))
        # Confirma los cambios
        connection.commit()
        if cursor.rowcount:
            # Si se eliminó, devuelve un mensaje de éxito
            return jsonify({"message": "Producto eliminado"})
        else:
            # Si no se encontró, devuelve un error 404
            return jsonify({"error": "Producto no encontrado"}), 404
    except mysql.connector.Error as err:
        # Devuelve un error si falla la consulta
        return jsonify({"error": "Error al eliminar el producto"}), 500
    finally:
        # Cierra el cursor
        cursor.close()
        # Cierra la conexión
        connection.close()