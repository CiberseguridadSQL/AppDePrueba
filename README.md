# Aplicacion Flask Vulnerable - Proyecto Academico

**ADVERTENCIA**: Esta aplicacion contiene vulnerabilidades de seguridad INTENCIONALES con propositos educativos. NO utilizar en produccion ni exponer a internet.

## Proposito

Este proyecto demuestra diferentes tipos de vulnerabilidades de inyeccion SQL para fines educativos a través de una interfaz web interactiva con formularios. Cada formulario representa un tipo diferente de ataque SQL injection.

## Características

✅ **Interfaz web completa** con formularios interactivos
✅ **6 tipos diferentes** de vulnerabilidades SQL Injection
✅ **Ejemplos de explotación** integrados en cada página
✅ **Visualización en tiempo real** de las queries ejecutadas
✅ **Documentación detallada** de cada vulnerabilidad

## Instalacion

### Opción 1: Si tienes Python instalado
```bash
pip install -r requirements.txt
python init_db.py
python app.py
```

### Opción 2: Si Python no está en el PATH
```bash
python -m pip install -r requirements.txt
python init_db.py
python app.py
```

### Opción 3: En Windows con py launcher
```powershell
py -m pip install -r requirements.txt
py init_db.py
py app.py
```

La aplicacion estara disponible en `http://localhost:5000`

Abre tu navegador y accede a la aplicación para ver la interfaz web con todos los formularios vulnerables.

## Vulnerabilidades Implementadas

Cada vulnerabilidad tiene su propia página web con un formulario interactivo donde puedes probar los ataques directamente.

### 1. UNION-based SQL Injection

**Formulario**: `/buscar_usuario` - 🔍 Búsqueda de Usuarios

**Descripcion**: Permite extraer datos de otras tablas usando la clausula UNION.

**Ejemplo de explotacion en el formulario**:
```
Campo "ID del Usuario": 1 UNION SELECT id,username,password,email FROM users--
```

**Como funciona**: El parametro `id` se concatena directamente en la query sin sanitizar, permitiendo agregar clausulas UNION para obtener datos de otras columnas.

**Codigo vulnerable**:
```python
query = f"SELECT id, username, email, role FROM users WHERE id = {user_id}"
```

**Proteccion**:
```python
cursor.execute("SELECT id, username, email, role FROM users WHERE id = ?", (user_id,))
```

---

### 2. Error-based SQL Injection

**Formulario**: `/buscar_nombre` - 🔎 Búsqueda por Nombre

**Descripcion**: Los mensajes de error de la base de datos revelan informacion sobre su estructura.

**Ejemplo de explotacion en el formulario**:
```
Campo "Nombre del Usuario": admin' AND 1=CAST((SELECT password FROM users LIMIT 1) AS INT)--
```

**Como funciona**: Al forzar errores de conversion de tipos, la base de datos muestra en el mensaje de error los datos que se intentaron convertir.

**Codigo vulnerable**:
```python
query = f"SELECT id, username, email FROM users WHERE username LIKE '%{name}%'"
```

**Proteccion**:
```python
cursor.execute("SELECT id, username, email FROM users WHERE username LIKE ?", (f'%{name}%',))
```

---

### 3. Boolean-based Blind SQL Injection

**Formulario**: `/login` - 🔐 Login de Usuarios

**Descripcion**: El atacante infiere datos basandose en respuestas verdadero/falso sin ver los datos directamente.

**Ejemplo de explotacion en el formulario**:
```
Campo "Usuario": admin'--
Campo "Contraseña": cualquier cosa
```
O para Blind SQL Injection:
```
Campo "Usuario": admin' AND (SELECT LENGTH(password) FROM users WHERE username='admin')>5--
Campo "Contraseña": x
```

**Como funciona**: Mediante queries que devuelven true o false, el atacante puede extraer datos caracter por caracter observando si el login es exitoso o no.

**Codigo vulnerable**:
```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

**Proteccion**:
```python
cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
```

---

### 4. Time-based Blind SQL Injection

**Formulario**: `/buscar_productos` - 🛍️ Búsqueda de Productos

**Descripcion**: El atacante infiere datos midiendo el tiempo de respuesta del servidor.

**Ejemplo de explotacion en el formulario**:
```
Campo "Categoría": electronics' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM users AS T1, users AS T2, users AS T3) ELSE 1 END)--
```

**Como funciona**: Ejecutando queries que toman mucho tiempo cuando una condicion es verdadera, el atacante puede extraer informacion bit a bit.

**Codigo vulnerable**:
```python
query = f"SELECT * FROM products WHERE category = '{category}'"
```

**Proteccion**:
```python
cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
```

---

### 5. Second-Order SQL Injection

**Formulario**: `/registro` - 📝 Registro de Usuarios

**Descripcion**: Los datos maliciosos se almacenan en la base de datos y se ejecutan en una query posterior.

**Como funciona**:
1. Se inserta un username malicioso: `admin'--`
2. Posteriormente, ese username se usa en otra query sin sanitizar
3. La inyeccion SQL se ejecuta en la segunda operacion

**Ejemplo de explotacion en el formulario**:
```
Campo "Nombre de Usuario": admin'--
Campo "Correo Electrónico": hacker@test.com
```

**Codigo vulnerable**:
```python
insert_query = f"INSERT INTO users (username, email, ...) VALUES ('{username}', '{email}', ...)"
select_query = f"SELECT * FROM users WHERE username = '{username}'"
```

**Proteccion**:
```python
cursor.execute("INSERT INTO users (username, email, ...) VALUES (?, ?, ...)", (username, email))
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

---

### 6. UPDATE SQL Injection

**Formulario**: `/actualizar_perfil` - ✏️ Actualizar Perfil

**Descripcion**: Permite modificar multiples campos en un UPDATE.

**Ejemplo de explotacion en el formulario**:
```
Campo "ID del Usuario": 2
Campo "Biografía": hacked', role='admin', password='pwned
```

**Como funciona**: Al inyectar comillas y comas, se pueden modificar campos adicionales en el UPDATE.

**Codigo vulnerable**:
```python
query = f"UPDATE users SET bio = '{bio}' WHERE id = {user_id}"
```

**Proteccion**:
```python
cursor.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, user_id))
```

---

## Principios de Proteccion contra SQL Injection

### 1. Prepared Statements (Parametrized Queries)
La forma mas efectiva de prevenir SQL injection:
```python
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### 2. Validacion de Entrada
Validar y sanitizar todas las entradas del usuario:
```python
if not user_id.isdigit():
    return error("ID invalido")
```

### 3. Principio de Minimo Privilegio
La cuenta de base de datos debe tener solo los permisos necesarios.

### 4. Escapado de Caracteres Especiales
Si no puedes usar prepared statements, escapa caracteres especiales:
```python
import re
username = re.escape(username)
```

### 5. ORM (Object-Relational Mapping)
Usar ORMs como SQLAlchemy que manejan la sanitizacion automaticamente:
```python
user = User.query.filter_by(id=user_id).first()
```

### 6. Lista Blanca para Valores Dinamicos
Para campos como ORDER BY, usar listas blancas:
```python
allowed_sorts = ['id', 'username', 'created_at']
if sort not in allowed_sorts:
    sort = 'id'
```

## Herramientas para Probar SQL Injection

- **sqlmap**: Herramienta automatizada para detectar y explotar SQL injection
- **Burp Suite**: Proxy para interceptar y modificar peticiones HTTP
- **OWASP ZAP**: Escaner de vulnerabilidades web

## Recursos Adicionales

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [SQLi Cheat Sheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Estructura de la Base de Datos

### Tabla: users
- id (INTEGER PRIMARY KEY)
- username (TEXT)
- password (TEXT)
- email (TEXT)
- role (TEXT)
- bio (TEXT)

### Tabla: products
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- category (TEXT)
- price (REAL)

### Tabla: orders
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER)
- product_id (INTEGER)
- quantity (INTEGER)
- total (REAL)

## Usuarios de Prueba

- admin:admin123 (role: admin)
- user1:pass123 (role: user)
- user2:mypassword (role: user)

## Licencia

Este proyecto es solo para fines educativos. Usar responsablemente.
