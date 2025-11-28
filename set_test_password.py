#!/usr/bin/env python3
"""
Script para establecer contraseña temporal de pruebas
"""

import docker
import subprocess
import sys

def set_test_password():
    """Establecer contraseña temporal para admin"""
    print("🔧 Configurando contraseña temporal para pruebas...")
    
    # Crear hash para la contraseña "123456"
    # En Flask-Login con Argon2, necesitamos generar el hash correcto
    
    sql_command = """
    UPDATE trabajador 
    SET password_hash = '$argon2id$v=19$m=65536,t=3,p=4$93eMYISc7e9wqinujP2iZg$0+P4tLeZdLy91eQToLyJR/VabDapUQ+R2C8rAiUfu'
    WHERE email = 'admin@sistema.local';
    """
    
    try:
        # Ejecutar comando MySQL
        result = subprocess.run([
            'docker', 'exec', 'mysql_db', 'mysql', 
            '-u', 'proyectos_admin', 
            '-p123456!#Td', 
            'proyectosDB',
            '-e', sql_command
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Contraseña temporal establecida")
            print("   Usuario: admin@sistema.local")
            print("   Contraseña: 123456")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

if __name__ == "__main__":
    set_test_password()