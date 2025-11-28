# Creación manual del usuario administrador

Para completar la configuración del sistema de autenticación, necesita crear manualmente el usuario administrador en la base de datos MySQL.

## Ejecute estos comandos SQL en su cliente MySQL:

```sql
-- 1. Conectarse a la base de datos
USE proyectosDB;

-- 2. Verificar si existe la columna rol
SHOW COLUMNS FROM trabajador LIKE 'rol';

-- 3. Si no existe, ejecutar la migración de estructura primero:
ALTER TABLE trabajador ADD COLUMN password_hash VARCHAR(255) NULL;
ALTER TABLE trabajador ADD COLUMN rol ENUM('superadmin', 'admin', 'supervisor', 'usuario') DEFAULT 'usuario' NOT NULL;
ALTER TABLE trabajador ADD COLUMN ultimo_acceso DATETIME NULL;
ALTER TABLE trabajador ADD COLUMN intentos_fallidos INT DEFAULT 0 NOT NULL;
ALTER TABLE trabajador ADD COLUMN bloqueado_hasta DATETIME NULL;

-- 4. Crear el usuario Super Administrador
INSERT INTO trabajador 
(nombre, email, profesion, rol, activo, password_hash, intentos_fallidos, created_at, updated_at)
VALUES 
('Super Administrador', 'admin@sistema.com', 'Super Administrador del Sistema', 
 'superadmin', TRUE, 'scrypt:32768:8:1$YourHashHere', 0, NOW(), NOW());

-- 5. Verificar que se creó correctamente
SELECT id, nombre, email, rol, activo FROM trabajador WHERE email = 'admin@sistema.com';
```

## Alternativa: Actualizar usuario existente

Si ya existe un trabajador que quiere convertir en administrador:

```sql
-- Buscar trabajadores existentes
SELECT id, nombre, email, activo FROM trabajador WHERE activo = TRUE;

-- Actualizar un trabajador existente (reemplace ID_DEL_TRABAJADOR con el ID real)
UPDATE trabajador 
SET rol = 'superadmin', 
    email = 'admin@sistema.com',
    password_hash = NULL,  -- Se configurará en el primer login
    activo = TRUE,
    updated_at = NOW()
WHERE id = ID_DEL_TRABAJADOR;
```

## Configuración inicial de contraseña

Después de crear el usuario administrador:

1. Inicie la aplicación: `python app.py`
2. Vaya a la página de login
3. Use:
   - **Email**: admin@sistema.com
   - **Contraseña**: (será configurada en el primer login)

## Estado actual del sistema

✅ **Completado:**
- Sistema de roles (SuperAdmin, Admin, Supervisor, Usuario)
- Autenticación con Argon2
- Protección contra ataques de fuerza bruta
- Formularios de login y gestión de usuarios
- Plantillas HTML responsivas
- Home página pública con login integrado
- Dashboard personalizado según roles

🔄 **Pendiente:**
- Creación del usuario administrador inicial
- Pruebas del sistema de autenticación

## Próximos pasos

1. Ejecute los comandos SQL para crear el usuario administrador
2. Instale las dependencias faltantes: `pip install Flask-Login Flask-WTF WTForms argon2-cffi`
3. Inicie la aplicación: `python app.py`
4. Pruebe el sistema de login

## Características del Sistema de Autenticación

- **4 roles diferentes**: SuperAdmin, Admin, Supervisor, Usuario
- **Seguridad Argon2**: Hash de contraseñas más seguro que bcrypt
- **Protección contra fuerza bruta**: Bloqueo automático después de 5 intentos fallidos
- **Página home pública**: Con login integrado y presentación del sistema
- **Dashboard personalizado**: Según el rol del usuario
- **Gestión completa de usuarios**: Para administradores
- **Formularios avanzados**: Con validación y UX mejorada
