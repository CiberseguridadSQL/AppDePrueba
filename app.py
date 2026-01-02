import sqlite3
import logging
import datetime
from flask import Flask, request, jsonify, render_template, has_request_context

app = Flask(__name__)
DATABASE = 'vulnerable.db'

# --- CONFIGURACIÓN BLUE TEAM ---
class ContextFilter(logging.Filter):
    def filter(self, record):
        if has_request_context():
            record.clientip = request.remote_addr
        else:
            record.clientip = 'SYSTEM'
        return True

# Configurar logging
file_handler = logging.FileHandler('security.log')
file_handler.setLevel(logging.INFO)
file_handler.addFilter(ContextFilter())
file_handler.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - IP: %(clientip)s - %(message)s'))

# Agregar handler al logger raiz
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger()
# -------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# --- IDS / DETECCIÓN DE ATAQUES ---
@app.before_request
def detect_attacks():
    # Firmas de ataques comunes (SQL Injection)
    attack_patterns = [
        "UNION SELECT", "UNION ALL SELECT", 
        "' OR '1'='1", "' OR 1=1", 
        "--", "/*", "Waitfor delay", 
        "admin' --", "DROP TABLE",
        " SELECT ", "CAST(", "CASE WHEN",
        "sqlite_master", " OR ", "SUBSTR(",
        "LENGTH(", "BENCHMARK(", "SLEEP("
    ]
    
    # Revisar argumentos de URL y datos de formularios
    data_to_check = list(request.args.values()) + list(request.form.values())
    
    for value in data_to_check:
        value_str = str(value).upper() # Convertir a mayúsculas para comparar
        
        for pattern in attack_patterns:
            if pattern.upper() in value_str:
                # ¡ALERTA DETECTADA!
                log_msg = f"ALERTA DE SEGURIDAD: Posible ataque SQL Injection detectado. Patron: '{pattern}' en Payload: '{value}'"
                logger.warning(log_msg)
                # Opcional: Podrías bloquear la petición aquí con "abort(403)"
                # Opcional: Podrías bloquear la petición aquí con "abort(403)"
# ----------------------------------


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/buscar_empleado', methods=['GET', 'POST'])
def buscar_empleado():
    """
    VULNERABILIDAD: Búsqueda unificada vulnerable a UNION-based y Error-based SQL Injection

    Esta ruta permite buscar empleados por ID o nombre en un formulario realista.
    - Búsqueda por ID: Vulnerable a UNION-based injection
    - Búsqueda por Nombre: Vulnerable a Error-based injection

    Ejemplos de explotación:
    ID: 1 UNION SELECT id,username,password,email FROM users--
    Nombre: admin' AND 1=CAST((SELECT password FROM users LIMIT 1) AS INT)--
    """
    result = None

    if request.method == 'POST':
        search_type = request.form.get('search_type', 'id')
        query_param = request.form.get('query', '')

        conn = get_db()
        cursor = conn.cursor()

        if search_type == 'id':
            # Búsqueda por ID - vulnerable a UNION-based injection
            query = f"SELECT id, username, email, role FROM users WHERE id = {query_param}"
        else:
            # Búsqueda por nombre - vulnerable a Error-based injection
            query = f"SELECT id, username, email, role FROM users WHERE username LIKE '%{query_param}%'"

        try:
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            users = []
            for row in results:
                users.append(dict(row))

            result = {
                'query': query,
                'users': users,
                'search_type': search_type
            }
        except Exception as e:
            result = {
                'error': str(e),
                'query': query,
                'users': [],
                'search_type': search_type
            }
    else:
        search_type = request.args.get('search_type', 'id') 
        query_param = request.args.get('query', '')
        conn = get_db()
        cursor = conn.cursor()
        if search_type=="id":
            query = f"SELECT id, username, email, role FROM users WHERE id = {query_param}"
        else:
            query = f"SELECT id, username, email, role FROM users WHERE username LIKE '%{query_param}%'"
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            users = []
            for row in results:
                users.append(dict(row))

            result = {
                'query': query,
                'users': users,
                'search_type': search_type
            }
        except Exception as e:
            result = {
                'error': str(e),
                'query': query,
                'users': [],
                'search_type': search_type
            }

    return render_template('buscar_empleado.html', result=result)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    VULNERABILIDAD 3: Boolean-based Blind SQL Injection

    El atacante puede inferir datos basandose en respuestas verdadero/falso.

    Ejemplo de explotacion:
    username: admin' AND (SELECT LENGTH(password) FROM users WHERE username='admin')>5--
    password: x
    """
    result = None

    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # LOG DEL INTENTO
        logger.info(f"Intento de inicio de sesión para usuario: {username}")

        conn = get_db()
        cursor = conn.cursor()

        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()

            if user:
                # LOG DE ÉXITO
                logger.info(f"✅ Login EXITOSO para usuario: {username}")
                result = {
                    'vulnerability': 'Boolean-based Blind SQL Injection',
                    'query': query,
                    'logged_in': True,
                    'user': dict(user)
                }
            else:
                # LOG DE FALLO
                logger.warning(f"❌ Login FALLIDO para usuario: {username} - Credenciales inválidas")
                result = {
                    'vulnerability': 'Boolean-based Blind SQL Injection',
                    'query': query,
                    'logged_in': False,
                    'message': 'Credenciales invalidas'
                }
        except Exception as e:
            # LOG DE ERROR (Indicio de Error-based SQLi)
            logger.error(f"🔥 ERROR DE BASE DE DATOS (Posible ataque): {str(e)}")
            result = {
                'error': str(e),
                'query': query,
                'logged_in': False
            }

    return render_template('login.html', result=result)


@app.route('/productos', methods=['GET', 'POST'])
def productos():
    """
    VULNERABILIDAD: Time-based Blind SQL Injection

    Catálogo de productos vulnerable a inyección SQL basada en tiempo.

    Ejemplo de explotación:
    category: electronics' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM users AS T1, users AS T2, users AS T3) ELSE 1 END)--
    """
    result = None

    if request.method == 'POST':
        category = request.form.get('category', '')

        conn = get_db()
        cursor = conn.cursor()

        query = f"SELECT * FROM products WHERE category = '{category}'"

        try:
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            products = []
            for row in results:
                products.append(dict(row))

            result = {
                'query': query,
                'products': products
            }
        except Exception as e:
            result = {
                'error': str(e),
                'query': query,
                'products': []
            }

    return render_template('productos.html', result=result)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    VULNERABILIDAD: Second-Order SQL Injection

    Registro de empleados vulnerable a inyección de segundo orden.

    Ejemplo de explotación:
    username: admin'--
    """
    result = None

    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')

        conn = get_db()
        cursor = conn.cursor()

        insert_query = f"INSERT INTO users (username, email, password, role) VALUES ('{username}', '{email}', 'default123', 'user')"

        try:
            cursor.execute(insert_query)
            user_id = cursor.lastrowid

            select_query = f"SELECT * FROM users WHERE username = '{username}'"
            cursor.execute(select_query)
            user = cursor.fetchone()

            conn.commit()
            conn.close()

            result = {
                'insert_query': insert_query,
                'select_query': select_query,
                'message': 'Empleado registrado exitosamente',
                'user': dict(user) if user else None
            }
        except Exception as e:
            conn.close()
            result = {
                'error': str(e),
                'insert_query': insert_query
            }

    return render_template('registro.html', result=result)


@app.route('/reportes')
def reportes():
    """Página de reportes (placeholder)"""
    return render_template('reportes.html')


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """
    VULNERABILIDAD: UPDATE SQL Injection

    Actualización de perfil vulnerable a inyección en UPDATE.

    Ejemplo de explotación:
    bio: hacked', role='admin', password='pwned
    """
    result = None

    if request.method == 'POST':
        user_id = request.form.get('user_id', '')
        bio = request.form.get('bio', '')

        conn = get_db()
        cursor = conn.cursor()

        query = f"UPDATE users SET bio = '{bio}' WHERE id = {user_id}"

        try:
            cursor.execute(query)
            conn.commit()

            cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
            user = cursor.fetchone()

            conn.close()

            result = {
                'query': query,
                'message': 'Perfil actualizado exitosamente',
                'user': dict(user) if user else None
            }
        except Exception as e:
            conn.close()
            result = {
                'error': str(e),
                'query': query
            }

    return render_template('perfil.html', result=result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
