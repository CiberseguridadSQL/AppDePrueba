import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
DATABASE = 'vulnerable.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


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

        conn = get_db()
        cursor = conn.cursor()

        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        try:
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()

            if user:
                result = {
                    'vulnerability': 'Boolean-based Blind SQL Injection',
                    'query': query,
                    'logged_in': True,
                    'user': dict(user)
                }
            else:
                result = {
                    'vulnerability': 'Boolean-based Blind SQL Injection',
                    'query': query,
                    'logged_in': False,
                    'message': 'Credenciales invalidas'
                }
        except Exception as e:
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
