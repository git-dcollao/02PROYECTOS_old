"""
Script para crear usuario administrador usando solo SQL
Sin dependencias de Python adicionales
"""

import mysql.connector
import os
from werkzeug.security import generate_password_hash

def create_admin_sql():
    """Crear usuario administrador usando conexión MySQL directa"""
    
    try:
        # Configuración de conexión usando credenciales del .env
        config = {
            'host': 'localhost',
            'port': 3308,  # Puerto del contenedor MySQL
            'user': 'proyectos_admin',
            'password': '123456!#Td',
            'database': 'proyectosDB',
            'charset': 'utf8mb4'
        }
        
        print(f"Conectando a la base de datos {config['database']}...")
        
        # Conectar a la base de datos
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Verificar si existe un superadmin
        cursor.execute("SELECT * FROM trabajador WHERE rol = 'superadmin' LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            # Generar hash de contraseña
            password_hash = generate_password_hash('admin123')
            
            # Verificar si existe usuario admin
            cursor.execute("SELECT * FROM trabajador WHERE email = 'admin@sistema.com' LIMIT 1")
            admin = cursor.fetchone()
            
            if admin:
                # Actualizar usuario existente
                cursor.execute("""
                    UPDATE trabajador 
                    SET rol = 'superadmin', 
                        activo = TRUE, 
                        password_hash = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (password_hash, admin[0]))
                
                print(f"✅ Usuario {admin[1]} actualizado como Super Administrador")
            else:
                # Crear nuevo super admin
                cursor.execute("""
                    INSERT INTO trabajador 
                    (nombre, email, profesion, rol, activo, password_hash, 
                     intentos_fallidos, created_at, updated_at)
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, ('Super Administrador', 'admin@sistema.com', 
                      'Super Administrador del Sistema', 'superadmin', True, 
                      password_hash, 0))
                
                print("✅ Super Administrador creado")
            
            # Confirmar cambios
            conn.commit()
            
            print("=" * 50)
            print("🎉 CONFIGURACIÓN COMPLETADA!")
            print("=" * 50)
            print("📧 Email: admin@sistema.com")
            print("🔒 Contraseña: admin123")
            print("👑 Rol: Super Administrador")
            print("=" * 50)
            print("⚠️  ¡IMPORTANTE!")
            print("   Cambie la contraseña después del primer login")
            print("=" * 50)
            
        else:
            print("ℹ️  Ya existe un Super Administrador en el sistema")
            
    except mysql.connector.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == '__main__':
    print("🚀 Creando Super Administrador...")
    print("-" * 50)
    
    success = create_admin_sql()
    
    if success:
        print("\n✅ ¡Todo listo!")
        print("   Ahora puede iniciar la aplicación y hacer login")
    else:
        print("\n❌ Hubo problemas en la configuración")
        print("   Verifique la conexión a la base de datos")
