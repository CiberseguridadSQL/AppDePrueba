"""
Aplicación Flask vulnerable que demuestra diferentes tipos de inyección SQL.
Este módulo contiene las rutas y funciones principales de la aplicación.
"""

import sqlite3
from flask import Flask, request, jsonify, render_template

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Nombre del archivo de base de datos SQLite
DATABASE = 'vulnerable.db'


def get_db():
    """
    Establece y retorna una conexión a la base de datos SQLite.
    
    Configura el row_factory para que los resultados se puedan acceder
    como diccionarios además de tuplas.
    
    Returns:
        sqlite3.Connection: Conexión a la base de datos configurada
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """
    Ruta principal de la aplicación.
    
    Renderiza la página de inicio que muestra el dashboard principal
    con todas las opciones disponibles del sistema.
    
    Returns:
        str: HTML renderizado de la página de inicio
    """
    return render_template('index.html')


@app.route('/buscar_empleado', methods=['GET', 'POST'])
def buscar_empleado():
    """
    Permite buscar empleados por ID o nombre en el directorio.
    
    Esta función acepta tanto solicitudes GET como POST para realizar
    búsquedas de empleados. Soporta dos tipos de búsqueda:
    - Por ID: Busca empleados mediante su identificador numérico
    - Por nombre: Busca empleados mediante coincidencia parcial del nombre de usuario
    
    La función construye consultas SQL directamente concatenando los parámetros
    de entrada, lo que la hace vulnerable a inyección SQL.
    
    Args:
        request.form o request.args: Contiene los parámetros de búsqueda:
            - search_type: Tipo de búsqueda ('id' o 'name')
            - query: Valor a buscar (ID numérico o nombre de usuario)
    
    Returns:
        str: HTML renderizado con los resultados de la búsqueda o mensajes de error
    """
    result = None

    # Procesar solicitud POST desde formulario
    if request.method == 'POST':
        search_type = request.form.get('search_type', 'id')
        query_param = request.form.get('query', '')

        conn = get_db()
        cursor = conn.cursor()

        # Construir consulta SQL según el tipo de búsqueda
        if search_type == 'id':
            # Búsqueda por ID numérico - vulnerable a inyección UNION-based
            query = f"SELECT id, username, email, role FROM users WHERE id = {query_param}"
        else:
            # Búsqueda por nombre - vulnerable a inyección Error-based
            query = f"SELECT id, username, email, role FROM users WHERE username LIKE '%{query_param}%'"

        try:
            # Ejecutar la consulta y obtener resultados
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            # Convertir los resultados de filas a diccionarios
            users = []
            for row in results:
                users.append(dict(row))

            # Preparar resultado para el template
            result = {
                'query': query,
                'users': users,
                'search_type': search_type
            }
        except Exception as e:
            # Manejar errores de ejecución de consulta
            result = {
                'error': str(e),
                'query': query,
                'users': [],
                'search_type': search_type
            }
    else:
        # Procesar solicitud GET desde URL
        search_type = request.args.get('search_type', 'id') 
        query_param = request.args.get('query', '')
        conn = get_db()
        cursor = conn.cursor()
        
        # Construir consulta SQL según el tipo de búsqueda
        if search_type == "id":
            query = f"SELECT id, username, email, role FROM users WHERE id = {query_param}"
        else:
            query = f"SELECT id, username, email, role FROM users WHERE username LIKE '%{query_param}%'"
            
        try:
            # Ejecutar la consulta y obtener resultados
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            # Convertir los resultados de filas a diccionarios
            users = []
            for row in results:
                users.append(dict(row))

            # Preparar resultado para el template
            result = {
                'query': query,
                'users': users,
                'search_type': search_type
            }
        except Exception as e:
            # Manejar errores de ejecución de consulta
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
    Maneja el proceso de autenticación de usuarios en el sistema.
    
    Permite a los usuarios iniciar sesión proporcionando su nombre de usuario
    y contraseña. La función valida las credenciales consultando la base de datos.
    
    La consulta SQL se construye directamente concatenando los valores de entrada,
    lo que permite inyección SQL basada en booleanos (blind SQL injection),
    donde un atacante puede inferir información basándose en respuestas verdadero/falso.
    
    Args:
        request.form: Contiene las credenciales:
            - username: Nombre de usuario
            - password: Contraseña del usuario
    
    Returns:
        str: HTML renderizado con el resultado del inicio de sesión
             o el formulario de login si no hay solicitud POST
    """
    result = None

    # Procesar solicitud POST de inicio de sesión
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = get_db()
        cursor = conn.cursor()

        # Construir consulta SQL directamente - vulnerable a inyección SQL
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        try:
            # Ejecutar consulta de autenticación
            cursor.execute(query)
            user = cursor.fetchone()
            conn.close()

            # Verificar si se encontró un usuario con las credenciales
            if user:
                result = {
                    'vulnerability': 'Boolean-based Blind SQL Injection',
                    'query': query,
                    'logged_in': True,
                    'user': dict(user)
                }
            else:
                # Credenciales inválidas
                result = {
                    'vulnerability': 'Boolean-based Blind SQL Injection',
                    'query': query,
                    'logged_in': False,
                    'message': 'Credenciales invalidas'
                }
        except Exception as e:
            # Manejar errores en la consulta
            result = {
                'error': str(e),
                'query': query,
                'logged_in': False
            }

    return render_template('login.html', result=result)


@app.route('/productos', methods=['GET', 'POST'])
def productos():
    """
    Muestra el catálogo de productos filtrado por categoría.
    
    Permite buscar productos en el sistema filtrándolos por su categoría.
    La función acepta solicitudes POST con el parámetro de categoría y
    retorna todos los productos que coincidan con la categoría especificada.
    
    La consulta SQL se construye directamente concatenando la categoría,
    lo que permite inyección SQL basada en tiempo (time-based blind SQL injection),
    donde un atacante puede extraer información basándose en el tiempo de respuesta.
    
    Args:
        request.form: Contiene el parámetro de búsqueda:
            - category: Categoría de productos a filtrar
    
    Returns:
        str: HTML renderizado con los productos encontrados o el formulario de búsqueda
    """
    result = None

    # Procesar solicitud POST de búsqueda de productos
    if request.method == 'POST':
        category = request.form.get('category', '')

        conn = get_db()
        cursor = conn.cursor()

        # Construir consulta SQL directamente - vulnerable a inyección SQL
        query = f"SELECT * FROM products WHERE category = '{category}'"

        try:
            # Ejecutar consulta y obtener productos
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            # Convertir resultados a diccionarios
            products = []
            for row in results:
                products.append(dict(row))

            # Preparar resultado para el template
            result = {
                'query': query,
                'products': products
            }
        except Exception as e:
            # Manejar errores en la consulta
            result = {
                'error': str(e),
                'query': query,
                'products': []
            }

    return render_template('productos.html', result=result)


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Registra nuevos empleados en el sistema.
    
    Permite crear nuevas cuentas de empleados proporcionando nombre de usuario
    y correo electrónico. La función inserta el nuevo registro en la base de datos
    y luego realiza una consulta SELECT para recuperar el usuario recién creado.
    
    Las consultas SQL se construyen directamente concatenando los valores de entrada,
    lo que permite inyección SQL de segundo orden, donde datos maliciosos almacenados
    se ejecutan en una consulta posterior.
    
    Args:
        request.form: Contiene los datos del nuevo empleado:
            - username: Nombre de usuario único
            - email: Correo electrónico corporativo
    
    Returns:
        str: HTML renderizado con el resultado del registro o el formulario de registro
    """
    result = None

    # Procesar solicitud POST de registro
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')

        conn = get_db()
        cursor = conn.cursor()

        # Construir consulta INSERT directamente - vulnerable a inyección SQL de segundo orden
        insert_query = f"INSERT INTO users (username, email, password, role) VALUES ('{username}', '{email}', 'default123', 'user')"

        try:
            # Insertar nuevo usuario en la base de datos
            cursor.execute(insert_query)
            user_id = cursor.lastrowid

            # Consultar el usuario recién creado - segunda consulta vulnerable
            select_query = f"SELECT * FROM users WHERE username = '{username}'"
            cursor.execute(select_query)
            user = cursor.fetchone()

            # Confirmar transacción y cerrar conexión
            conn.commit()
            conn.close()

            # Preparar resultado exitoso
            result = {
                'insert_query': insert_query,
                'select_query': select_query,
                'message': 'Empleado registrado exitosamente',
                'user': dict(user) if user else None
            }
        except Exception as e:
            # Manejar errores y cerrar conexión
            conn.close()
            result = {
                'error': str(e),
                'insert_query': insert_query
            }

    return render_template('registro.html', result=result)


@app.route('/reportes')
def reportes():
    """
    Muestra la página de reportes del sistema.
    
    Esta ruta renderiza la página de reportes, que actualmente
    es un placeholder para futuras funcionalidades de generación de reportes.
    
    Returns:
        str: HTML renderizado de la página de reportes
    """
    return render_template('reportes.html')


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """
    Permite actualizar el perfil de un usuario en el sistema.
    
    Permite a los usuarios modificar su biografía personal. La función
    actualiza el campo 'bio' del usuario especificado mediante su ID.
    
    La consulta SQL UPDATE se construye directamente concatenando los valores,
    lo que permite inyección SQL en operaciones UPDATE, permitiendo modificar
    otros campos de la base de datos además del campo 'bio'.
    
    Args:
        request.form: Contiene los datos a actualizar:
            - user_id: Identificador numérico del usuario
            - bio: Nueva biografía del usuario
    
    Returns:
        str: HTML renderizado con el resultado de la actualización o el formulario
    """
    result = None

    # Procesar solicitud POST de actualización de perfil
    if request.method == 'POST':
        user_id = request.form.get('user_id', '')
        bio = request.form.get('bio', '')

        conn = get_db()
        cursor = conn.cursor()

        # Construir consulta UPDATE directamente - vulnerable a inyección SQL
        query = f"UPDATE users SET bio = '{bio}' WHERE id = {user_id}"

        try:
            # Ejecutar actualización de perfil
            cursor.execute(query)
            conn.commit()

            # Consultar usuario actualizado
            cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
            user = cursor.fetchone()

            conn.close()

            # Preparar resultado exitoso
            result = {
                'query': query,
                'message': 'Perfil actualizado exitosamente',
                'user': dict(user) if user else None
            }
        except Exception as e:
            # Manejar errores y cerrar conexión
            conn.close()
            result = {
                'error': str(e),
                'query': query
            }

    return render_template('perfil.html', result=result)


if __name__ == '__main__':
    """
    Punto de entrada principal de la aplicación.
    
    Inicia el servidor Flask en modo debug, escuchando en todas
    las interfaces de red (0.0.0.0) en el puerto 5000.
    """
    app.run(debug=True, host='0.0.0.0', port=5000)
