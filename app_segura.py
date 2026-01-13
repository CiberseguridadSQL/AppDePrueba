"""
Aplicación Flask segura que implementa buenas prácticas de seguridad.
Este módulo utiliza prepared statements (consultas parametrizadas) y validación
de entrada para prevenir inyección SQL y otros ataques comunes.
"""

import sqlite3
import re
from flask import Flask, request, jsonify

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Nombre del archivo de base de datos SQLite
DATABASE = 'vulnerable.db'


def get_db():
    """
    Establece y retorna una conexión segura a la base de datos SQLite.
    
    Configura el row_factory para que los resultados se puedan acceder
    como diccionarios además de tuplas.
    
    Returns:
        sqlite3.Connection: Conexión a la base de datos configurada
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def validate_integer(value, field_name="campo"):
    """
    Valida que un valor sea un entero válido.
    
    Verifica que el valor proporcionado sea numérico y lo convierte
    a entero. Si el valor no es válido, lanza una excepción.
    
    Args:
        value: Valor a validar (puede ser string o número)
        field_name: Nombre del campo para mensajes de error personalizados
    
    Returns:
        int: El valor convertido a entero
    
    Raises:
        ValueError: Si el valor no es un entero válido
    """
    if not str(value).isdigit():
        raise ValueError(f"{field_name} debe ser un numero entero")
    return int(value)


def validate_string(value, max_length=100):
    """
    Valida y limita la longitud de una cadena de texto.
    
    Verifica que el valor sea una cadena de texto y la trunca
    a la longitud máxima especificada para prevenir ataques de
    desbordamiento de buffer.
    
    Args:
        value: Valor a validar (debe ser string)
        max_length: Longitud máxima permitida para la cadena
    
    Returns:
        str: La cadena validada y truncada a max_length
    
    Raises:
        ValueError: Si el valor no es una cadena de texto
    """
    if not isinstance(value, str):
        raise ValueError("Valor debe ser texto")
    return value[:max_length]


@app.route('/')
def index():
    """
    Muestra la página de inicio de la aplicación segura.
    
    Renderiza una página HTML simple que explica que esta versión
    utiliza prepared statements y validación de entrada, y lista
    todos los endpoints disponibles del sistema.
    
    Returns:
        str: HTML con la información de la aplicación y endpoints disponibles
    """
    return '''
    <h1>Aplicacion Flask SEGURA - Version Corregida</h1>
    <p>Esta version usa prepared statements y validacion de entrada.</p>
    <h2>Endpoints seguros:</h2>
    <ul>
        <li><strong>GET /users?id=1</strong> - Consulta segura con prepared statements</li>
        <li><strong>GET /search?name=admin</strong> - Busqueda segura</li>
        <li><strong>GET /login?username=admin&password=pass</strong> - Login seguro</li>
        <li><strong>GET /products?category=electronics</strong> - Consulta parametrizada</li>
        <li><strong>POST /register</strong> - Registro seguro</li>
        <li><strong>POST /update_profile</strong> - Update seguro</li>
    </ul>
    '''


@app.route('/users', methods=['GET'])
def get_user():
    """
    Obtiene información de un usuario por su ID de forma segura.
    
    Esta función utiliza prepared statements (consultas parametrizadas)
    para prevenir inyección SQL. El ID del usuario se valida antes de
    ejecutar la consulta para asegurar que sea un entero válido.
    
    Args:
        request.args: Parámetros de la URL:
            - id: Identificador numérico del usuario a buscar
    
    Returns:
        JSON: Respuesta con los usuarios encontrados o error de validación
    """
    user_id = request.args.get('id', '')

    # Validar que el ID sea un entero válido
    try:
        user_id = validate_integer(user_id, "ID de usuario")
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Usar prepared statement para prevenir inyección SQL
    cursor.execute(
        "SELECT id, username, email, role FROM users WHERE id = ?",
        (user_id,)
    )

    results = cursor.fetchall()
    conn.close()

    # Convertir resultados a diccionarios
    users = [dict(row) for row in results]

    return jsonify({
        'method': 'Prepared Statement',
        'secure': True,
        'results': users
    })


@app.route('/search', methods=['GET'])
def search_user():
    """
    Busca usuarios por nombre de forma segura usando LIKE.
    
    Permite buscar usuarios mediante coincidencia parcial del nombre.
    Utiliza prepared statements con el operador LIKE para realizar
    búsquedas seguras que previenen inyección SQL.
    
    Args:
        request.args: Parámetros de la URL:
            - name: Nombre de usuario a buscar (coincidencia parcial)
    
    Returns:
        JSON: Respuesta con los usuarios encontrados que coinciden con la búsqueda
    """
    name = request.args.get('name', '')
    # Validar y limitar la longitud del nombre
    name = validate_string(name, 50)

    conn = get_db()
    cursor = conn.cursor()

    # Usar prepared statement con LIKE para búsqueda segura
    cursor.execute(
        "SELECT id, username, email FROM users WHERE username LIKE ?",
        (f'%{name}%',)
    )

    results = cursor.fetchall()
    conn.close()

    # Convertir resultados a diccionarios
    users = [dict(row) for row in results]

    return jsonify({
        'method': 'Prepared Statement',
        'secure': True,
        'results': users
    })


@app.route('/login', methods=['GET'])
def login():
    """
    Autentica usuarios de forma segura utilizando prepared statements.
    
    Valida las credenciales del usuario consultando la base de datos
    con consultas parametrizadas. Las credenciales se validan antes
    de ejecutar la consulta para limitar su longitud.
    
    NOTA: En producción, las contraseñas deben estar hasheadas usando
    algoritmos seguros como bcrypt o argon2, nunca almacenadas en texto plano.
    
    Args:
        request.args: Parámetros de la URL:
            - username: Nombre de usuario
            - password: Contraseña del usuario
    
    Returns:
        JSON: Respuesta con el resultado del inicio de sesión y datos del usuario
    """
    username = request.args.get('username', '')
    password = request.args.get('password', '')

    # Validar y limitar la longitud de las credenciales
    username = validate_string(username, 50)
    password = validate_string(password, 100)

    conn = get_db()
    cursor = conn.cursor()

    # Usar prepared statement para autenticación segura
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    result = cursor.fetchone()
    conn.close()

    # Verificar si se encontraron credenciales válidas
    if result:
        return jsonify({
            'method': 'Prepared Statement',
            'secure': True,
            'logged_in': True,
            'user': {
                'id': result['id'],
                'username': result['username'],
                'role': result['role']
            }
        })
    else:
        # Credenciales inválidas
        return jsonify({
            'method': 'Prepared Statement',
            'secure': True,
            'logged_in': False,
            'message': 'Credenciales invalidas'
        })


@app.route('/products', methods=['GET'])
def get_products():
    """
    Obtiene productos filtrados por categoría de forma segura.
    
    Retorna todos los productos que pertenecen a una categoría específica.
    Utiliza prepared statements para prevenir inyección SQL y valida
    la longitud de la categoría antes de ejecutar la consulta.
    
    Args:
        request.args: Parámetros de la URL:
            - category: Categoría de productos a filtrar
    
    Returns:
        JSON: Respuesta con los productos encontrados en la categoría especificada
    """
    category = request.args.get('category', '')
    # Validar y limitar la longitud de la categoría
    category = validate_string(category, 50)

    conn = get_db()
    cursor = conn.cursor()

    # Usar prepared statement para consulta segura
    cursor.execute(
        "SELECT * FROM products WHERE category = ?",
        (category,)
    )

    results = cursor.fetchall()
    conn.close()

    # Convertir resultados a diccionarios
    products = [dict(row) for row in results]

    return jsonify({
        'method': 'Prepared Statement',
        'secure': True,
        'results': products
    })


@app.route('/register', methods=['POST'])
def register():
    """
    Registra nuevos usuarios de forma segura usando prepared statements.
    
    Crea un nuevo usuario en el sistema después de validar los datos de entrada.
    Realiza validación de formato de email usando expresiones regulares y
    utiliza prepared statements tanto para INSERT como para SELECT para
    prevenir inyección SQL de segundo orden.
    
    Args:
        request.json: Datos JSON del nuevo usuario:
            - username: Nombre de usuario único
            - email: Correo electrónico válido
    
    Returns:
        JSON: Respuesta con el resultado del registro y datos del usuario creado
    """
    data = request.get_json()

    # Validar y sanitizar datos de entrada
    try:
        username = validate_string(data.get('username', ''), 50)
        email = validate_string(data.get('email', ''), 100)

        # Verificar que los campos requeridos estén presentes
        if not username or not email:
            raise ValueError("Username y email son requeridos")

        # Validar formato de email con expresión regular
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValueError("Email invalido")

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Usar prepared statement para INSERT seguro
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, 'default123', 'user')
        )

        user_id = cursor.lastrowid

        # Usar prepared statement para SELECT seguro
        cursor.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )

        result = cursor.fetchone()
        conn.commit()

        return jsonify({
            'method': 'Prepared Statement',
            'secure': True,
            'message': 'Usuario registrado correctamente',
            'user': dict(result) if result else None
        })

    except sqlite3.IntegrityError:
        # Manejar error de usuario duplicado
        return jsonify({'error': 'Usuario ya existe'}), 409
    finally:
        # Asegurar cierre de conexión
        conn.close()


@app.route('/update_profile', methods=['POST'])
def update_profile():
    """
    Actualiza el perfil de un usuario de forma segura.
    
    Permite modificar la biografía de un usuario utilizando prepared statements
    en la consulta UPDATE. Los datos de entrada se validan antes de ejecutar
    la consulta para prevenir inyección SQL.
    
    Args:
        request.json: Datos JSON con la información a actualizar:
            - user_id: Identificador numérico del usuario
            - bio: Nueva biografía del usuario (máximo 500 caracteres)
    
    Returns:
        JSON: Respuesta con el resultado de la actualización y datos del usuario actualizado
    """
    data = request.get_json()

    # Validar datos de entrada
    try:
        user_id = validate_integer(data.get('user_id', ''), "User ID")
        bio = validate_string(data.get('bio', ''), 500)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        # Usar prepared statement para UPDATE seguro
        cursor.execute(
            "UPDATE users SET bio = ? WHERE id = ?",
            (bio, user_id)
        )

        # Consultar usuario actualizado
        cursor.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )

        result = cursor.fetchone()
        conn.commit()

        return jsonify({
            'method': 'Prepared Statement',
            'secure': True,
            'message': 'Perfil actualizado correctamente',
            'user': dict(result) if result else None
        })

    finally:
        # Asegurar cierre de conexión
        conn.close()


@app.route('/orders', methods=['GET'])
def get_orders():
    """
    Obtiene órdenes ordenadas por un campo específico usando lista blanca.
    
    Retorna todas las órdenes ordenadas por el campo especificado.
    Como ORDER BY no puede usar placeholders (?) en SQL, se utiliza
    validación de lista blanca (whitelist) para permitir solo campos
    válidos y prevenir inyección SQL.
    
    Args:
        request.args: Parámetros de la URL:
            - sort: Campo por el cual ordenar (debe estar en la lista blanca)
    
    Returns:
        JSON: Respuesta con las órdenes ordenadas o error si el campo no es válido
    """
    sort_by = request.args.get('sort', 'id')

    # Lista blanca de campos permitidos para ordenamiento
    ALLOWED_SORT_FIELDS = ['id', 'user_id', 'product_id', 'quantity', 'total']

    # Validar que el campo de ordenamiento esté en la lista blanca
    if sort_by not in ALLOWED_SORT_FIELDS:
        return jsonify({
            'error': 'Campo de ordenamiento invalido',
            'allowed_fields': ALLOWED_SORT_FIELDS
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    # Construir consulta con campo validado (seguro porque está en whitelist)
    query = f"SELECT * FROM orders ORDER BY {sort_by}"

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    # Convertir resultados a diccionarios
    orders = [dict(row) for row in results]

    return jsonify({
        'method': 'Whitelist validation',
        'secure': True,
        'sort_by': sort_by,
        'results': orders
    })


@app.errorhandler(Exception)
def handle_error(error):
    """
    Maneja errores de forma segura sin revelar información sensible.
    
    Captura todas las excepciones no manejadas y retorna un mensaje
    genérico al cliente, mientras registra el error completo en los
    logs del servidor para diagnóstico interno.
    
    Args:
        error: Excepción capturada
    
    Returns:
        JSON: Respuesta de error genérica sin detalles internos
    """
    # Registrar error completo en logs del servidor
    app.logger.error(f"Error: {str(error)}")

    # Retornar mensaje genérico al cliente
    return jsonify({
        'error': 'Ha ocurrido un error en el servidor',
        'message': 'Por favor contacta al administrador'
    }), 500


if __name__ == '__main__':
    """
    Punto de entrada principal de la aplicación segura.
    
    Inicia el servidor Flask sin modo debug (más seguro para producción)
    escuchando en todas las interfaces de red (0.0.0.0) en el puerto 5001.
    """
    app.run(debug=False, host='0.0.0.0', port=5001)
