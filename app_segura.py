import sqlite3
import re
from flask import Flask, request, jsonify

app = Flask(__name__)
DATABASE = 'vulnerable.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def validate_integer(value, field_name="campo"):
    """Valida que el valor sea un entero valido"""
    if not str(value).isdigit():
        raise ValueError(f"{field_name} debe ser un numero entero")
    return int(value)


def validate_string(value, max_length=100):
    """Valida y limita la longitud de strings"""
    if not isinstance(value, str):
        raise ValueError("Valor debe ser texto")
    return value[:max_length]


@app.route('/')
def index():
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
    VERSION SEGURA: Usa prepared statements (parametrized queries)
    """
    user_id = request.args.get('id', '')

    try:
        user_id = validate_integer(user_id, "ID de usuario")
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email, role FROM users WHERE id = ?",
        (user_id,)
    )

    results = cursor.fetchall()
    conn.close()

    users = [dict(row) for row in results]

    return jsonify({
        'method': 'Prepared Statement',
        'secure': True,
        'results': users
    })


@app.route('/search', methods=['GET'])
def search_user():
    """
    VERSION SEGURA: Prepared statements con LIKE
    """
    name = request.args.get('name', '')
    name = validate_string(name, 50)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email FROM users WHERE username LIKE ?",
        (f'%{name}%',)
    )

    results = cursor.fetchall()
    conn.close()

    users = [dict(row) for row in results]

    return jsonify({
        'method': 'Prepared Statement',
        'secure': True,
        'results': users
    })


@app.route('/login', methods=['GET'])
def login():
    """
    VERSION SEGURA: Prepared statements para autenticacion
    NOTA: En produccion, las contraseñas deben estar hasheadas (bcrypt, argon2)
    """
    username = request.args.get('username', '')
    password = request.args.get('password', '')

    username = validate_string(username, 50)
    password = validate_string(password, 100)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    result = cursor.fetchone()
    conn.close()

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
        return jsonify({
            'method': 'Prepared Statement',
            'secure': True,
            'logged_in': False,
            'message': 'Credenciales invalidas'
        })


@app.route('/products', methods=['GET'])
def get_products():
    """
    VERSION SEGURA: Prepared statements
    """
    category = request.args.get('category', '')
    category = validate_string(category, 50)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM products WHERE category = ?",
        (category,)
    )

    results = cursor.fetchall()
    conn.close()

    products = [dict(row) for row in results]

    return jsonify({
        'method': 'Prepared Statement',
        'secure': True,
        'results': products
    })


@app.route('/register', methods=['POST'])
def register():
    """
    VERSION SEGURA: Prepared statements en INSERT y SELECT
    """
    data = request.get_json()

    try:
        username = validate_string(data.get('username', ''), 50)
        email = validate_string(data.get('email', ''), 100)

        if not username or not email:
            raise ValueError("Username y email son requeridos")

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValueError("Email invalido")

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, 'default123', 'user')
        )

        user_id = cursor.lastrowid

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
        return jsonify({'error': 'Usuario ya existe'}), 409
    finally:
        conn.close()


@app.route('/update_profile', methods=['POST'])
def update_profile():
    """
    VERSION SEGURA: Prepared statements en UPDATE
    """
    data = request.get_json()

    try:
        user_id = validate_integer(data.get('user_id', ''), "User ID")
        bio = validate_string(data.get('bio', ''), 500)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "UPDATE users SET bio = ? WHERE id = ?",
            (bio, user_id)
        )

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
        conn.close()


@app.route('/orders', methods=['GET'])
def get_orders():
    """
    VERSION SEGURA: Lista blanca para ORDER BY

    Como ORDER BY no puede usar placeholders (?), usamos lista blanca
    """
    sort_by = request.args.get('sort', 'id')

    ALLOWED_SORT_FIELDS = ['id', 'user_id', 'product_id', 'quantity', 'total']

    if sort_by not in ALLOWED_SORT_FIELDS:
        return jsonify({
            'error': 'Campo de ordenamiento invalido',
            'allowed_fields': ALLOWED_SORT_FIELDS
        }), 400

    conn = get_db()
    cursor = conn.cursor()

    query = f"SELECT * FROM orders ORDER BY {sort_by}"

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

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
    Manejo seguro de errores - no revelar detalles internos
    """
    app.logger.error(f"Error: {str(error)}")

    return jsonify({
        'error': 'Ha ocurrido un error en el servidor',
        'message': 'Por favor contacta al administrador'
    }), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)
