# Crear entorno virtual
    ' python -m venv venv '
# Activar entorno virtual
    ' ./venv/Scripts/activate ' 
# Desactivar entorno
    ' ./venv/Scripts/deactivate '
# Eliminar entorno virtual llamado "venv"
    ' Remove-Item -Recurse -Force venv '
# Instalar dependencias
    ' pip install Flask Flask-Migrate python-dotenv '
# Instalar requirements.txt 
    '  pip install -r requirements.txt '
# Guardar o actualizar requirements.txt
    ' pip freeze > requirements.txt '
    
# Detener servidores del docker-compose del proyecto
    ' docker-compose down 
     docker-compose build    
     docker-compose up -d '
# ewvisar archivo logs con errores del docker proyectos_app
    ' docker-compose logs proyectos_app '