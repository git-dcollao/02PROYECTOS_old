from flask import Blueprint, request, jsonify, send_file, current_app, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
import subprocess
import json
import gzip
import zipfile
import tempfile
import shutil
import traceback
import io
import time
import pymysql
import psutil
from functools import wraps
from app import db
from app.models import UserRole
import logging

# Configurar logging específico para backups
backup_logger = logging.getLogger('backup')

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """Decorador que requiere privilegios de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        
        if not current_user.can_manage_users():
            return jsonify({'success': False, 'message': 'Permisos insuficientes'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def superadmin_required(f):
    """Decorador que requiere privilegios de SUPERADMIN para operaciones críticas como backups"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'No autenticado'}), 401
        
        if not current_user.is_superadmin():
            return jsonify({'success': False, 'message': 'Acceso restringido - Solo SUPERADMIN'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


class BackupManager:
    """Clase para manejar operaciones de backup"""
    
    def __init__(self):
        self.backup_dir = os.path.join(os.getcwd(), 'backups')
        self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """Asegurar que el directorio de backups existe"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            backup_logger.info(f"Directorio de backups creado: {self.backup_dir}")
    
    def get_db_config(self):
        """Obtener configuración de la base de datos"""
        config = current_app.config
        return {
            'host': config.get('MYSQL_HOST', 'mysql_db'),
            'port': 3306,  # Puerto interno del container MySQL
            'user': config.get('MYSQL_USER', 'proyectos_admin'),
            'password': config.get('MYSQL_PASSWORD', '123456!#Td'),
            'database': config.get('MYSQL_DATABASE', 'proyectosDB')
        }
    
    def generate_backup_filename(self, custom_name=None, compress=True):
        """Generar nombre único para el backup"""
        backup_logger.info(f"generate_backup_filename llamado con: custom_name='{custom_name}', compress={compress}")
        
        if custom_name:
            # Limpiar nombre personalizado
            clean_name = "".join(c for c in custom_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_name = clean_name.replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{clean_name}_{timestamp}"
            backup_logger.info(f"Nombre personalizado generado: '{filename}'")
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"backup_{timestamp}"
            backup_logger.info(f"Nombre automático generado: '{filename}'")
        
        extension = '.sql.gz' if compress else '.sql'
        final_filename = filename + extension
        backup_logger.info(f"Nombre final del archivo: '{final_filename}'")
        return final_filename
    
    def create_backup(self, backup_name=None, description=None, include_data=True, compress=True):
        """Crear backup de la base de datos"""
        try:
            db_config = self.get_db_config()
            filename = self.generate_backup_filename(backup_name, compress)
            filepath = os.path.join(self.backup_dir, filename)
            
            backup_logger.info(f"Configuración DB para backup: {db_config}")
            
            # Preparar comando mysqldump
            cmd = [
                'mysqldump',
                f'--host={db_config["host"]}',
                f'--port={db_config["port"]}',
                f'--user={db_config["user"]}',
                f'--password={db_config["password"]}',
                '--skip-ssl',  # Cambio de --ssl-mode=DISABLED a --skip-ssl
                '--single-transaction',
                '--routines',
                '--triggers',
                '--lock-tables=false',   # Evitar bloqueos, sin timeout personalizado
                '--no-tablespaces'       # Evitar error de privilegios de tablespaces
            ]
            
            if not include_data:
                cmd.append('--no-data')
            
            cmd.append(db_config['database'])
            
            backup_logger.info(f"Comando mysqldump: {' '.join(cmd).replace(db_config['password'], '***')}")
            backup_logger.info(f"Iniciando backup: {filename}")
            
            # Ejecutar mysqldump con timeout
            backup_logger.info("Ejecutando mysqldump...")
            
            # Ejecutar mysqldump y capturar la salida
            process = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                timeout=300  # 5 minutos de timeout
            )
            
            backup_logger.info(f"Proceso mysqldump terminado con código: {process.returncode}")
            
            if process.returncode != 0:
                error_msg = process.stderr
                backup_logger.error(f"Error en mysqldump: {error_msg}")
                raise Exception(f"Error en mysqldump: {error_msg}")
            
            # Verificar que tenemos datos
            if not process.stdout or len(process.stdout.strip()) == 0:
                raise Exception("El mysqldump no produjo datos")
                
            backup_logger.info(f"Datos capturados: {len(process.stdout)} caracteres")
            
            # Escribir los datos al archivo
            if compress:
                with gzip.open(filepath, 'wt', encoding='utf-8') as f:
                    f.write(process.stdout)
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(process.stdout)
            
            # Verificar que el archivo se creó correctamente
            if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                raise Exception("El archivo de backup está vacío o no se creó")
            
            # Crear metadata
            metadata = {
                'filename': filename,
                'name': backup_name or filename,  # Para compatibilidad con el frontend
                'original_name': backup_name or filename,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'created_by': getattr(current_user, 'nombre', 'Sistema') if hasattr(current_user, 'nombre') else 'Sistema',
                'user_id': getattr(current_user, 'id', None) if hasattr(current_user, 'id') else None,
                'size': os.path.getsize(filepath),
                'compressed': compress,
                'include_data': include_data,
                'status': 'success'
            }
            
            self.save_metadata(filename, metadata)
            
            backup_logger.info(f"Backup creado exitosamente: {filename} ({metadata['size']} bytes)")
            
            return {
                'success': True,
                'filename': filename,
                'size': metadata['size'],
                'message': 'Backup creado exitosamente'
            }
            
        except Exception as e:
            backup_logger.error(f"Error creando backup: {str(e)}")
            
            # Limpiar archivo parcial si existe
            if 'filepath' in locals() and os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            
            return {
                'success': False,
                'message': f'Error al crear backup: {str(e)}'
            }
    
    def restore_backup(self, file_source, is_upload=False, db_config=None):
        """Restaurar backup desde archivo"""
        try:
            # Usar configuración pasada como parámetro o obtenerla
            if db_config is None:
                db_config = self.get_db_config()
            
            if is_upload:
                # Es un archivo subido
                temp_dir = tempfile.mkdtemp()
                temp_file = os.path.join(temp_dir, 'restore_backup.sql')
                
                try:
                    # Detectar si realmente es un archivo comprimido
                    file_source.seek(0)  # Volver al inicio del archivo
                    header = file_source.read(3)  # Leer los primeros 3 bytes
                    file_source.seek(0)  # Volver al inicio
                    
                    # Verificar si es realmente gzip (magic bytes: 1f 8b 08)
                    is_gzip = header[:2] == b'\x1f\x8b'
                    
                    if is_gzip:
                        backup_logger.info("Archivo detectado como gzip válido")
                        with gzip.open(file_source, 'rt') as gz_file:
                            with open(temp_file, 'w') as out_file:
                                shutil.copyfileobj(gz_file, out_file)
                    elif file_source.filename.endswith('.zip'):
                        backup_logger.info("Archivo detectado como ZIP")
                        with zipfile.ZipFile(file_source, 'r') as zip_file:
                            # Buscar primer archivo .sql en el zip
                            sql_files = [f for f in zip_file.namelist() if f.endswith('.sql')]
                            if not sql_files:
                                raise Exception("No se encontró archivo .sql en el ZIP")
                            
                            with zip_file.open(sql_files[0]) as sql_file:
                                with open(temp_file, 'wb') as out_file:
                                    shutil.copyfileobj(sql_file, out_file)
                    else:
                        # Archivo .sql normal (no comprimido)
                        backup_logger.info(f"Archivo detectado como SQL plano (header: {header})")
                        file_source.save(temp_file)
                    
                    sql_file_path = temp_file
                    
                finally:
                    # El directorio temporal se limpiará al final
                    pass
            else:
                # Es un archivo existente en el servidor
                filepath = os.path.join(self.backup_dir, file_source)
                
                if not os.path.exists(filepath):
                    raise Exception("Archivo de backup no encontrado")
                
                # Detectar si realmente es un archivo gzip
                is_gzip = False
                try:
                    with open(filepath, 'rb') as f:
                        header = f.read(2)
                        is_gzip = header == b'\x1f\x8b'
                except:
                    is_gzip = False
                
                if is_gzip:
                    # Descomprimir temporalmente
                    backup_logger.info("Archivo detectado como gzip válido en servidor")
                    temp_dir = tempfile.mkdtemp()
                    temp_file = os.path.join(temp_dir, 'restore_backup.sql')
                    
                    with gzip.open(filepath, 'rt') as gz_file:
                        with open(temp_file, 'w') as out_file:
                            shutil.copyfileobj(gz_file, out_file)
                    
                    sql_file_path = temp_file
                else:
                    # Archivo SQL plano
                    backup_logger.info("Archivo detectado como SQL plano en servidor")
                    sql_file_path = filepath
                    temp_dir = None
            
            backup_logger.info(f"Iniciando restauración desde: {sql_file_path}")
            
            # Leer el contenido del archivo de manera segura
            backup_logger.info("Leyendo contenido del archivo de backup...")
            
            # Detectar encoding del archivo leyendo los primeros bytes
            with open(sql_file_path, 'rb') as f:
                raw_start = f.read(4)
            
            # Detectar BOM (Byte Order Mark) para UTF-16
            detected_encoding = 'utf-8'
            if raw_start[:2] == b'\xff\xfe':  # UTF-16 LE BOM
                detected_encoding = 'utf-16-le'
                backup_logger.info("⚠️ Detectado archivo UTF-16 LE con BOM - convirtiendo a UTF-8...")
            elif raw_start[:2] == b'\xfe\xff':  # UTF-16 BE BOM
                detected_encoding = 'utf-16-be'
                backup_logger.info("⚠️ Detectado archivo UTF-16 BE con BOM - convirtiendo a UTF-8...")
            elif raw_start[:3] == b'\xef\xbb\xbf':  # UTF-8 BOM
                detected_encoding = 'utf-8-sig'
                backup_logger.info("⚠️ Detectado archivo UTF-8 con BOM - removiendo BOM...")
            elif raw_start[:2] == b'\x1f\x8b':  # GZIP
                backup_logger.info("Detectado archivo comprimido GZIP...")
                detected_encoding = 'gzip'
            
            try:
                if detected_encoding == 'gzip':
                    with open(sql_file_path, 'rb') as f:
                        backup_content = gzip.decompress(f.read()).decode('utf-8')
                    backup_logger.info(f"Archivo GZIP descomprimido: {len(backup_content)} caracteres")
                else:
                    # Leer con el encoding detectado
                    with open(sql_file_path, 'r', encoding=detected_encoding) as f:
                        backup_content = f.read()
                    backup_logger.info(f"Contenido del backup leído con {detected_encoding}: {len(backup_content)} caracteres")
                
                # Eliminar BOM si está presente (puede quedar después de decodificar UTF-16 o UTF-8-sig)
                if backup_content.startswith('\ufeff'):
                    backup_content = backup_content[1:]
                    backup_logger.info("✅ BOM Unicode eliminado del contenido")

                # Envolver el contenido con SET FOREIGN_KEY_CHECKS=0/1
                backup_content = (
                    "SET FOREIGN_KEY_CHECKS=0;\n"
                    + backup_content +
                    "\nSET FOREIGN_KEY_CHECKS=1;"
                )
            except UnicodeDecodeError as e:
                backup_logger.warning(f"Error UTF-8 en posición {e.start}: {e.reason}")
                backup_logger.info("Intentando detectar si es un archivo gzip mal etiquetado...")
                
                # Si falla UTF-8, verificar si realmente es gzip
                with open(sql_file_path, 'rb') as f:
                    raw_content = f.read()
                
                # Verificar magic bytes de gzip
                if raw_content[:2] == b'\x1f\x8b':
                    backup_logger.info("Archivo detectado como gzip después del error UTF-8, descomprimiendo...")
                    try:
                        import io
                        backup_content = gzip.decompress(raw_content).decode('utf-8')
                        backup_logger.info(f"Descompresión exitosa: {len(backup_content)} caracteres")
                    except Exception as gz_error:
                        backup_logger.error(f"Error al descomprimir: {gz_error}")
                        raise Exception(f"Error al procesar archivo: no es UTF-8 válido ni gzip válido")
                else:
                    # Intentar lectura con diferentes codificaciones
                    encodings = ['utf-16-le', 'utf-16-be', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
                    decoded = False
                    for encoding in encodings:
                        try:
                            backup_content = raw_content.decode(encoding)
                            backup_logger.info(f"Archivo decodificado exitosamente con {encoding}: {len(backup_content)} caracteres")
                            decoded = True
                            break
                        except:
                            continue
                    
                    if not decoded:
                        raise Exception(f"No se pudo decodificar el archivo con ninguna codificación estándar")
            
            # Intentar primero con PyMySQL directo (más confiable)
            try:
                backup_logger.info("Iniciando restauración con PyMySQL directo...")
                import pymysql
                
                backup_logger.info("Conectando con PyMySQL...")
                connection = pymysql.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database'],
                    charset='utf8mb4',
                    connect_timeout=30,
                    read_timeout=120,
                    write_timeout=120,
                    autocommit=False
                )
                
                backup_logger.info("Ejecutando SQL con PyMySQL optimizado...")
                
                # Configurar conexión para operaciones largas
                connection.ping(reconnect=True)
                
                with connection.cursor() as cursor:
                    # Configurar para operaciones batch
                    cursor.execute("SET SESSION wait_timeout = 300")
                    cursor.execute("SET SESSION interactive_timeout = 300")
                    cursor.execute("SET SESSION net_read_timeout = 120")
                    cursor.execute("SET SESSION net_write_timeout = 120")
                    cursor.execute("SET autocommit = 0")
                    

                    # Parser robusto: split por punto y coma fuera de cadenas y comentarios
                    def split_sql_statements(sql):
                        statements = []
                        statement = ''
                        in_string = False
                        string_char = ''
                        in_single_line_comment = False
                        in_multi_line_comment = False
                        prev_char = ''
                        i = 0
                        while i < len(sql):
                            char = sql[i]
                            next_char = sql[i+1] if i+1 < len(sql) else ''
                            # Manejo de comentarios
                            if in_single_line_comment:
                                if char == '\n':
                                    in_single_line_comment = False
                                    statement += char
                                i += 1
                                continue
                            if in_multi_line_comment:
                                if char == '*' and next_char == '/':
                                    in_multi_line_comment = False
                                    i += 2
                                    continue
                                i += 1
                                continue
                            # Iniciar comentario
                            if not in_string and char == '-' and next_char == '-':
                                in_single_line_comment = True
                                i += 2
                                continue
                            if not in_string and char == '/' and next_char == '*':
                                in_multi_line_comment = True
                                i += 2
                                continue
                            # Manejo de cadenas
                            if not in_string and char in ('"', "'"):
                                in_string = True
                                string_char = char
                                statement += char
                                i += 1
                                continue
                            if in_string and char == string_char:
                                if prev_char != '\\':
                                    in_string = False
                                statement += char
                                i += 1
                                continue
                            # Split por punto y coma fuera de cadena/comentario
                            if not in_string and char == ';':
                                if statement.strip():
                                    statements.append(statement.strip())
                                statement = ''
                                i += 1
                                continue
                            statement += char
                            prev_char = char
                            i += 1
                        if statement.strip():
                            statements.append(statement.strip())
                        # No filtrar ningún statement, ejecutar todos
                        return [s for s in statements if s]

                    statements = split_sql_statements(backup_content)
                    backup_logger.info(f"Procesando {len(statements)} statements SQL en lotes...")
                    
                    # Filtrar statements problemáticos
                    def should_skip_statement(stmt):
                        stmt_upper = stmt.strip().upper()
                        # Ignorar comentarios MySQL especiales que dan error
                        if stmt.strip().startswith('/*!') and stmt.strip().endswith('*/'):
                            return True
                        # Ignorar comentarios regulares
                        if stmt_upper.startswith('--'):
                            return True
                        # Ignorar statements vacíos o solo whitespace
                        if not stmt.strip():
                            return True
                        return False
                    
                    filtered_statements = [s for s in statements if not should_skip_statement(s)]
                    backup_logger.info(f"Filtrados {len(statements) - len(filtered_statements)} statements problemáticos, quedan {len(filtered_statements)}")
                    
                    executed = 0
                    skipped = 0
                    batch_size = 25  # Procesar en lotes más pequeños
                    

                    for i in range(0, len(filtered_statements), batch_size):
                        batch = filtered_statements[i:i + batch_size]
                        backup_logger.info(f"Procesando lote {i//batch_size + 1}/{(len(filtered_statements) + batch_size - 1)//batch_size}")
                        for stmt in batch:
                            if stmt:
                                try:
                                    cursor.execute(stmt)
                                    executed += 1
                                except Exception as stmt_error:
                                    err_str = str(stmt_error)
                                    # Solo registrar primeros 20 errores para no saturar logs
                                    if skipped < 20:
                                        backup_logger.warning(f"Error ejecutando statement: {stmt[:80]}... -> {err_str}")
                                    skipped += 1
                        try:
                            connection.commit()
                        except Exception as commit_error:
                            backup_logger.warning(f"Error en commit del lote: {commit_error}")
                            connection.rollback()
                    
                    backup_logger.info(f"Restauración completada: {executed} statements ejecutados, {skipped} omitidos por errores")
                    
                    # Si no se ejecutó nada, lanzar excepción para usar método de respaldo
                    if executed == 0:
                        raise Exception("No se ejecutó ningún statement con éxito, usando método de respaldo")
                
                connection.close()
                        
            except Exception as pymysql_error:
                backup_logger.warning(f"PyMySQL falló: {pymysql_error}")
                backup_logger.info("Intentando restauración con comando mysql como respaldo...")
                
                # Método de respaldo usando comando mysql
                try:
                    cmd = [
                        'mysql',
                        f'--host={db_config["host"]}',
                        f'--port={db_config["port"]}',
                        f'--user={db_config["user"]}',
                        f'--password={db_config["password"]}',
                        '--skip-ssl',
                        db_config['database']
                    ]
                    
                    backup_logger.info(f"Ejecutando comando mysql de respaldo...")
                    
                    # Ejecutar comando con timeout de 5 minutos
                    process = subprocess.run(
                        cmd, 
                        input=backup_content,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True,
                        timeout=300
                    )
                    
                    backup_logger.info(f"Comando ejecutado, código de retorno: {process.returncode}")
                    
                    if process.returncode != 0:
                        error_msg = process.stderr if process.stderr else "Error desconocido"
                        backup_logger.error(f"Error en mysql: {error_msg}")
                        raise Exception(f"Comando mysql falló: {error_msg}")
                    
                    backup_logger.info("Restauración con comando mysql completada")
                    
                except Exception as mysql_error:
                    backup_logger.error(f"Error con comando mysql: {mysql_error}")
                    raise Exception(f"Error en restauración (ambos métodos fallaron): PyMySQL: {pymysql_error}, MySQL: {mysql_error}")
                
            # Limpiar archivos temporales
            if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            backup_logger.info("Restauración completada exitosamente")
            
            return {
                'success': True,
                'message': 'Base de datos restaurada exitosamente'
            }
            
        except subprocess.TimeoutExpired:
            backup_logger.error("Timeout en proceso de restauración MySQL")
            
            # Limpiar archivos temporales
            if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            
            return {
                'success': False,
                'message': 'La restauración excedió el tiempo límite (3 minutos). El archivo puede ser muy grande o hay un problema de conectividad.'
            }
            
        except Exception as e:
            backup_logger.error(f"Error restaurando backup: {str(e)}")
            
            # Limpiar archivos temporales en caso de error
            if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
            
            return {
                'success': False,
                'message': f'Error al restaurar backup: {str(e)}'
            }
    
    def list_backups(self):
        """Listar todos los backups disponibles"""
        try:
            backups = []
            
            if not os.path.exists(self.backup_dir):
                return []
            
            for filename in os.listdir(self.backup_dir):
                if filename.endswith(('.sql', '.sql.gz')):
                    filepath = os.path.join(self.backup_dir, filename)
                    
                    # Cargar metadata si existe
                    metadata = self.load_metadata(filename)
                    
                    if metadata:
                        backups.append(metadata)
                    else:
                        # Crear metadata básica para archivos sin metadata
                        stat = os.stat(filepath)
                        backups.append({
                            'filename': filename,
                            'name': filename,  # Para compatibilidad con el frontend
                            'original_name': filename,
                            'description': 'Backup sin metadata',
                            'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'created_by': 'Desconocido',
                            'size': stat.st_size,
                            'compressed': filename.endswith('.gz'),
                            'status': 'success'
                        })
            
            # Ordenar por fecha de creación (más reciente primero)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            backup_logger.error(f"Error listando backups: {str(e)}")
            return []
    
    def delete_backup(self, filename):
        """Eliminar un backup específico"""
        try:
            filepath = os.path.join(self.backup_dir, filename)
            metadata_path = self.get_metadata_path(filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                backup_logger.info(f"Backup eliminado: {filename}")
            
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return {
                'success': True,
                'message': 'Backup eliminado exitosamente'
            }
            
        except Exception as e:
            backup_logger.error(f"Error eliminando backup {filename}: {str(e)}")
            return {
                'success': False,
                'message': f'Error al eliminar backup: {str(e)}'
            }
    
    def clean_old_backups(self, days=30, keep_minimum=5):
        """Limpiar backups antiguos manteniendo un mínimo"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_minimum:
                return {
                    'success': True,
                    'deleted_count': 0,
                    'message': f'Se mantienen {len(backups)} backups (mínimo requerido: {keep_minimum})'
                }
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            # Ordenar por fecha (más reciente primero)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            # Mantener los keep_minimum más recientes, eliminar los antiguos
            for i, backup in enumerate(backups):
                if i >= keep_minimum:  # No tocar los más recientes
                    backup_date = datetime.fromisoformat(backup['created_at'].replace('Z', '+00:00'))
                    if backup_date < cutoff_date:
                        result = self.delete_backup(backup['filename'])
                        if result['success']:
                            deleted_count += 1
            
            backup_logger.info(f"Limpieza completada: {deleted_count} backups eliminados")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'message': f'{deleted_count} backups antiguos eliminados'
            }
            
        except Exception as e:
            backup_logger.error(f"Error limpiando backups antiguos: {str(e)}")
            return {
                'success': False,
                'message': f'Error al limpiar backups: {str(e)}'
            }
    
    def get_stats(self):
        """Obtener estadísticas de backups"""
        try:
            backups = self.list_backups()
            
            total_size = sum(b['size'] for b in backups)
            last_backup = backups[0]['created_at'] if backups else None
            
            # Verificar estado de la base de datos
            try:
                from sqlalchemy import text
                with db.engine.connect() as connection:
                    connection.execute(text('SELECT 1'))
                db_status = 'Conectado'
            except:
                db_status = 'Error'
            
            return {
                'success': True,
                'stats': {
                    'total_backups': len(backups),
                    'total_size': total_size,
                    'last_backup_date': last_backup,
                    'db_status': db_status
                }
            }
            
        except Exception as e:
            backup_logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener estadísticas: {str(e)}'
            }
    
    def save_metadata(self, filename, metadata):
        """Guardar metadata del backup"""
        metadata_path = self.get_metadata_path(filename)
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            backup_logger.warning(f"No se pudo guardar metadata para {filename}: {str(e)}")
    
    def load_metadata(self, filename):
        """Cargar metadata del backup"""
        metadata_path = self.get_metadata_path(filename)
        try:
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                # Normalizar metadata para compatibilidad
                # Si tiene upload_timestamp pero no created_at, convertir
                if 'upload_timestamp' in metadata and 'created_at' not in metadata:
                    metadata['created_at'] = metadata['upload_timestamp']
                
                # Asegurar que tenga todos los campos requeridos
                if 'created_at' not in metadata:
                    # Usar fecha de modificación del archivo como fallback
                    filepath = os.path.join(self.backup_dir, filename)
                    if os.path.exists(filepath):
                        stat = os.stat(filepath)
                        metadata['created_at'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # Campos requeridos con valores por defecto
                metadata.setdefault('filename', filename)
                metadata.setdefault('name', filename)
                metadata.setdefault('description', metadata.get('original_filename', 'Sin descripción'))
                metadata.setdefault('created_by', metadata.get('uploaded_by', 'Desconocido'))
                metadata.setdefault('status', 'success')
                
                # Obtener tamaño del archivo si no está en metadata
                if 'size' not in metadata or 'file_size' in metadata:
                    metadata['size'] = metadata.get('file_size', 0)
                
                # Determinar si está comprimido
                metadata['compressed'] = filename.endswith('.gz')
                
                return metadata
                
        except Exception as e:
            backup_logger.warning(f"No se pudo cargar metadata para {filename}: {str(e)}")
        return None
    
    def get_metadata_path(self, filename):
        """Obtener ruta del archivo de metadata"""
        return os.path.join(self.backup_dir, f"{filename}.meta")


# Instancia global del manager
backup_manager = BackupManager()


@admin_bp.route('/backup')
@admin_bp.route('/gestion_backup')  # Ruta alternativa para compatibilidad
@login_required
@superadmin_required
def backup_page():
    """Página principal de gestión de backups"""
    return render_template('admin/gestion_backup.html')


@admin_bp.route('/backup/v2')
@login_required
@superadmin_required
def backup_page_v2():
    """Página refactorizada de gestión de backups - Versión 2"""
    backup_logger.info(f"📋 Usuario {current_user.email} accedió a Backup Manager V2")
    return render_template('admin/backup_manager_v2.html')


@admin_bp.route('/backup/download/<filename>')
@superadmin_required
def download_backup(filename):
    """Descargar un archivo de backup"""
    try:
        backup_manager = BackupManager()
        backup_dir = backup_manager.backup_dir
        filepath = os.path.join(backup_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'message': 'Archivo de backup no encontrado'}), 404
        
        # Verificar que el archivo esté dentro del directorio de backups (seguridad)
        if not os.path.abspath(filepath).startswith(os.path.abspath(backup_dir)):
            return jsonify({'success': False, 'message': 'Acceso no autorizado'}), 403
        
        backup_logger.info(f"Descargando backup: {filename}")
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/gzip' if filename.endswith('.gz') else 'application/sql'
        )
        
    except Exception as e:
        backup_logger.error(f"Error descargando backup {filename}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al descargar: {str(e)}'}), 500

@admin_bp.route('/backup/create', methods=['POST'])
@login_required
@superadmin_required
def create_backup():
    """Crear nuevo backup"""
    try:
        backup_logger.info("Iniciando creación de backup desde web interface")
        backup_logger.info(f"Form data completo: {dict(request.form)}")
        backup_logger.info(f"Form files: {dict(request.files)}")
        
        backup_name = request.form.get('name', '').strip()  # Cambiado de 'backup_name' a 'name'
        description = request.form.get('description', '').strip()
        
        # IMPORTANTE: Por defecto incluir datos y comprimir (valores seguros)
        # Si el campo viene, comparar con 'on', si no viene, usar True por defecto
        include_data_param = request.form.get('include_data', 'on')
        compress_param = request.form.get('compress', 'on')
        
        include_data = include_data_param == 'on'
        compress = compress_param == 'on'
        
        backup_logger.info(f"Parámetros recibidos: name='{backup_name}', desc='{description}', include_data_raw='{include_data_param}', compress_raw='{compress_param}'")
        backup_logger.info(f"Parámetros procesados: data={include_data}, compress={compress}")
        
        # Debug: Verificar configuración de base de datos
        db_config = backup_manager.get_db_config()
        backup_logger.info(f"Configuración DB: {db_config}")
        
        result = backup_manager.create_backup(
            backup_name=backup_name if backup_name else None,
            description=description if description else None,
            include_data=include_data,
            compress=compress
        )
        
        backup_logger.info(f"Resultado backup: {result}")
        return jsonify(result)
        
    except Exception as e:
        backup_logger.error(f"Error en create_backup endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/restore', methods=['POST'])
@login_required
@superadmin_required
def restore_backup():
    """Restaurar backup desde archivo subido"""
    try:
        if 'backup_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No se proporcionó archivo de backup'
            }), 400
        
        file = request.files['backup_file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No se seleccionó archivo'
            }), 400
        
        # Obtener configuración antes de la restauración
        db_config = backup_manager.get_db_config()
        result = backup_manager.restore_backup(file, is_upload=True, db_config=db_config)
        return jsonify(result)
        
    except Exception as e:
        backup_logger.error(f"Error en restore_backup endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/restore-file', methods=['POST'])
@login_required
@admin_required
def restore_backup_file():
    """Restaurar backup desde archivo existente en servidor - VERSIÓN MEJORADA"""
    try:
        backup_logger.info("🚀 === INICIO RESTAURACIÓN MEJORADA ===")
        
        data = request.get_json()
        filename = data.get('filename') if data else None
        clean_database = data.get('clean_database', False) if data else False
        
        if not filename:
            backup_logger.error("❌ No se especificó archivo")
            return jsonify({
                'success': False,
                'message': 'No se especificó archivo'
            }), 400
        
        backup_logger.info(f"📁 Iniciando restauración de archivo: {filename}")
        backup_logger.info(f"🧹 Limpieza de base de datos: {'SÍ' if clean_database else 'NO'}")
        
        # Importar el servicio mejorado
        from app.services.backup_service import enhanced_backup_service
        
        # Configurar timeout en la respuesta
        from threading import Thread
        import queue
        import time
        
        # Crear cola para resultado
        result_queue = queue.Queue()
        
        # Obtener configuración ANTES del hilo para evitar problemas de contexto
        db_config = backup_manager.get_db_config()
        
        def enhanced_restore_task():
            """Tarea de restauración con servicio mejorado"""
            try:
                backup_logger.info(f"🔧 Iniciando tarea de restauración MEJORADA para: {filename}")
                
                # Usar el servicio mejorado con opción de limpieza
                result = enhanced_backup_service.restore_backup_enhanced(
                    filename, 
                    is_upload=False, 
                    db_config=db_config,
                    clean_database=clean_database
                )
                
                backup_logger.info(f"✅ Tarea de restauración MEJORADA completada: {result}")
                result_queue.put(('success', result))
                
            except Exception as e:
                backup_logger.error(f"💥 Error en tarea de restauración MEJORADA: {str(e)}")
                backup_logger.error(f"📍 Traceback: {traceback.format_exc()}")
                result_queue.put(('error', str(e)))
        
        # Ejecutar en hilo separado con servicio mejorado
        thread = Thread(target=enhanced_restore_task, name=f"BackupRestore-{filename}")
        thread.daemon = True
        thread.start()
        
        backup_logger.info(f"🧵 Hilo de restauración iniciado: {thread.name}")
        
        # Esperar resultado con timeout de 20 minutos (backups grandes)
        try:
            status, result = result_queue.get(timeout=1200)  # 20 minutos
            
            if status == 'success':
                backup_logger.info(f"🎉 Resultado de restauración EXITOSA: {result}")
                
                # FIX #8: Commit explícito de SQLAlchemy para evitar rollback posterior
                try:
                    from app import db
                    db.session.commit()
                    backup_logger.info("✅ SQLAlchemy session commited después de restauración")
                except Exception as commit_err:
                    backup_logger.warning(f"⚠️ No se pudo hacer commit SQLAlchemy: {str(commit_err)}")
                
                return jsonify(result)
            else:
                backup_logger.error(f"❌ Error en restauración: {result}")
                return jsonify({
                    'success': False,
                    'message': f'Error en restauración: {result}'
                }), 500
                
        except queue.Empty:
            backup_logger.error("⏰ Timeout en restauración después de 20 minutos")
            return jsonify({
                'success': False,
                'message': 'La restauración está tomando demasiado tiempo (>20min). Revise los logs del servidor para más detalles.'
            }), 408
        
    except Exception as e:
        backup_logger.error(f"💥 Error en restore_backup_file endpoint MEJORADO: {str(e)}")
        backup_logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/progress', methods=['GET'])
@login_required
@admin_required
def get_backup_progress():
    """Endpoint para obtener progreso en tiempo real de operaciones de backup"""
    try:
        from app.services.backup_service import enhanced_backup_service
        
        tracker = enhanced_backup_service.progress_tracker
        
        if tracker is None:
            return jsonify({
                'success': True,
                'progress': {
                    'current_operation': 'Sin operación activa',
                    'progress_percent': 0,
                    'elapsed_time': '0s',
                    'last_update_ago': '0s',
                    'details': {},
                    'is_active': False
                }
            })
        
        # Calcular tiempo transcurrido
        elapsed_time = time.time() - tracker.start_time
        last_update_ago = time.time() - tracker.last_update
        
        # Determinar si hay operación activa
        is_active = last_update_ago < 30  # Activo si última actualización fue hace menos de 30s
        
        progress_data = {
            'current_operation': tracker.current_operation,
            'progress_percent': tracker.progress_percent,
            'elapsed_time': f"{elapsed_time:.1f}s",
            'last_update_ago': f"{last_update_ago:.1f}s",
            'details': tracker.details,
            'is_active': is_active
        }
        
        # Debug log
        backup_logger.debug(f"📊 Progreso solicitado: {progress_data['progress_percent']}% - {progress_data['current_operation']}")
        
        return jsonify({
            'success': True,
            'progress': progress_data
        })
        
    except Exception as e:
        backup_logger.error(f"Error obteniendo progreso: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'progress': {
                'current_operation': 'Error obteniendo progreso',
                'progress_percent': 0,
                'elapsed_time': '0s',
                'last_update_ago': '0s',
                'details': {},
                'is_active': False
            }
        }), 500


@admin_bp.route('/backup/debug/db-status', methods=['GET'])
@login_required
@superadmin_required
def debug_database_status():
    """Debug: Estado actual de la base de datos"""
    try:
        db_config = backup_manager.get_db_config()
        connection = pymysql.connect(**db_config, connect_timeout=5)
        
        with connection.cursor() as cursor:
            # Contar tablas
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", 
                         (db_config['database'],))
            table_count = cursor.fetchone()[0]
            
            # Contar registros en tablas principales
            tables_info = []
            main_tables = ['trabajador', 'requerimiento', 'actividad_proyecto', 'area', 'estado', 'prioridad']
            
            for table in main_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    tables_info.append({'table': table, 'rows': count})
                except Exception as e:
                    tables_info.append({'table': table, 'rows': f'Error: {str(e)}'})
            
            # Últimas actualizaciones
            cursor.execute("""
                SELECT table_name, update_time 
                FROM information_schema.tables 
                WHERE table_schema = %s AND update_time IS NOT NULL
                ORDER BY update_time DESC LIMIT 5
            """, (db_config['database'],))
            
            recent_updates = []
            for row in cursor.fetchall():
                recent_updates.append({
                    'table': row[0],
                    'updated': row[1].strftime('%Y-%m-%d %H:%M:%S') if row[1] else 'N/A'
                })
            
        connection.close()
        
        return jsonify({
            'success': True,
            'database_status': {
                'total_tables': table_count,
                'main_tables': tables_info,
                'recent_updates': recent_updates,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        backup_logger.error(f"Error obteniendo estado de BD: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@admin_bp.route('/backup/system-status', methods=['GET'])
@login_required
@superadmin_required
def get_backup_system_status():
    """Endpoint para obtener estado simplificado del sistema (para UI V2)"""
    try:
        backup_manager = BackupManager()
        
        # Estado de la base de datos
        db_status = "Conectado"
        try:
            db_config = backup_manager.get_db_config()
            connection = pymysql.connect(**db_config, connect_timeout=5)
            connection.close()
        except Exception as db_error:
            backup_logger.warning(f"Error conectando a DB para status: {db_error}")
            db_status = "Desconectado"
        
        return jsonify({
            'success': True,
            'status': {
                'database_status': db_status
            }
        })
        
    except Exception as e:
        backup_logger.error(f"Error obteniendo estado del sistema: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/backup/system-status-full', methods=['GET'])
@login_required
@admin_required
def get_backup_system_status_full():
    """Endpoint completo para obtener estado del sistema de backup (legacy)"""
    try:
        import psutil
        import pymysql  # Importar pymysql aquí
        
        # Información del sistema
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        # Estado de la base de datos
        try:
            db_config = backup_manager.get_db_config()
            connection = pymysql.connect(**db_config, connect_timeout=5)
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s", 
                             (db_config['database'],))
                table_count = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, (db_config['database'],))
                db_size_mb = cursor.fetchone()[0] or 0
            
            connection.close()
            db_status = 'connected'
            
        except Exception as db_error:
            backup_logger.warning(f"Error conectando a DB para status: {db_error}")
            table_count = 0
            db_size_mb = 0
            db_status = 'disconnected'
        
        # Información del directorio de backups
        backup_dir = backup_manager.backup_dir
        backup_files = []
        total_backup_size = 0
        
        if os.path.exists(backup_dir):
            for file in os.listdir(backup_dir):
                if file.endswith(('.sql', '.sql.gz', '.zip')):
                    filepath = os.path.join(backup_dir, file)
                    size = os.path.getsize(filepath)
                    total_backup_size += size
                    backup_files.append({
                        'name': file,
                        'size_mb': round(size / 1024 / 1024, 2),
                        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        return jsonify({
            'success': True,
            'system_status': {
                'server_resources': {
                    'cpu_percent': cpu,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
                    'disk_free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                    'disk_percent': round(disk.used / disk.total * 100, 1)
                },
                'database_status': {
                    'status': db_status,
                    'table_count': table_count,
                    'size_mb': db_size_mb,
                    'connection_config': {
                        'host': db_config.get('host', 'N/A'),
                        'port': db_config.get('port', 'N/A'),
                        'database': db_config.get('database', 'N/A')
                    }
                },
                'backup_directory': {
                    'path': backup_dir,
                    'exists': os.path.exists(backup_dir),
                    'file_count': len(backup_files),
                    'total_size_mb': round(total_backup_size / 1024 / 1024, 2),
                    'recent_files': sorted(backup_files, key=lambda x: x['modified'], reverse=True)[:5]
                }
            }
        })
        
    except Exception as e:
        backup_logger.error(f"Error obteniendo estado del sistema: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/backup/test')
@login_required
@admin_required
def test_backup_system():
    """Endpoint de diagnóstico para el sistema de backup"""
    try:
        backup_logger.info("🔧 Test del sistema de backup solicitado")
        
        # Test básico
        backup_dir_exists = os.path.exists(backup_manager.backup_dir)
        backup_logger.info(f"📂 Directorio de backup existe: {backup_dir_exists}")
        
        # Contar archivos
        if backup_dir_exists:
            files = [f for f in os.listdir(backup_manager.backup_dir) if f.endswith(('.sql', '.sql.gz'))]
            backup_logger.info(f"📋 Archivos de backup encontrados: {len(files)}")
        else:
            files = []
        
        return jsonify({
            'success': True,
            'message': 'Sistema de backup funcionando',
            'backup_dir_exists': backup_dir_exists,
            'backup_files_count': len(files),
            'backup_files': files[:5]  # Solo primeros 5
        })
        
    except Exception as e:
        backup_logger.error(f"❌ Error en test del sistema: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@admin_bp.route('/backup/list')
@login_required
@superadmin_required
def list_backups():
    """Listar backups disponibles con estadísticas"""
    try:
        backup_logger.info("Solicitando lista de backups...")
        backup_logger.info(f"Usuario autenticado: {current_user.is_authenticated}")
        backup_logger.info(f"Usuario actual: {getattr(current_user, 'email', 'No email')}")
        
        backups = backup_manager.list_backups()
        backup_logger.info(f"Se encontraron {len(backups)} backups")
        
        # Calcular estadísticas
        total_size = sum(b.get('size', 0) for b in backups)
        last_backup = backups[0]['created_at'] if backups else '-'
        
        def format_size(bytes_size):
            """Formatear tamaño de archivo"""
            if bytes_size == 0:
                return '0 B'
            k = 1024
            sizes = ['B', 'KB', 'MB', 'GB']
            i = 0
            size = float(bytes_size)
            while size >= k and i < len(sizes) - 1:
                size /= k
                i += 1
            return f'{size:.2f} {sizes[i]}'
        
        return jsonify({
            'success': True,
            'backups': backups,
            'stats': {
                'total_backups': len(backups),
                'total_size': format_size(total_size),
                'last_backup_date': last_backup
            }
        })
        
    except Exception as e:
        backup_logger.error(f"Error en list_backups endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/debug-list')
def debug_list_backups():
    """Endpoint de debug sin autenticación para verificar backend"""
    try:
        backup_logger.info("DEBUG: Solicitando lista de backups sin auth...")
        backups = backup_manager.list_backups()
        backup_logger.info(f"DEBUG: Se encontraron {len(backups)} backups")
        return jsonify({
            'success': True,
            'backups': backups,
            'debug': True
        })
        
    except Exception as e:
        backup_logger.error(f"ERROR DEBUG: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/delete/<filename>', methods=['DELETE'])
@login_required
@admin_required
def delete_backup(filename):
    """Eliminar backup específico"""
    try:
        result = backup_manager.delete_backup(filename)
        return jsonify(result)
        
    except Exception as e:
        backup_logger.error(f"Error en delete_backup endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/clean-old', methods=['POST'])
@login_required
@admin_required
def clean_old_backups():
    """Limpiar backups antiguos"""
    try:
        result = backup_manager.clean_old_backups()
        return jsonify(result)
        
    except Exception as e:
        backup_logger.error(f"Error en clean_old_backups endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/stats')
@login_required
@admin_required
def backup_stats():
    """Obtener estadísticas de backups"""
    try:
        result = backup_manager.get_stats()
        return jsonify(result)
        
    except Exception as e:
        backup_logger.error(f"Error en backup_stats endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@admin_bp.route('/backup/upload', methods=['POST'])
@login_required
@admin_required
def upload_backup():
    """Subir archivo de backup desde el disco duro del usuario"""
    try:
        backup_logger.info("Iniciando upload de backup desde archivo local")
        
        # Verificar que se haya enviado un archivo
        if 'backup_file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No se seleccionó ningún archivo'
            }), 400
        
        file = request.files['backup_file']
        
        # Verificar que el archivo tenga nombre
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No se seleccionó ningún archivo'
            }), 400
        
        # Verificar extensión del archivo
        allowed_extensions = {'.sql', '.sql.gz', '.gz'}
        file_ext = ''.join([ext for ext in allowed_extensions if file.filename.lower().endswith(ext.replace('.', ''))])
        
        if not any(file.filename.lower().endswith(ext.replace('.', '')) for ext in allowed_extensions):
            return jsonify({
                'success': False,
                'message': 'Tipo de archivo no válido. Solo se permiten archivos .sql, .sql.gz o .gz'
            }), 400
        
        # Generar nombre único para evitar conflictos
        original_name = file.filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name_without_ext = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
        
        # Limpiar nombre
        clean_name = "".join(c for c in name_without_ext if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')
        
        # Crear nombre final
        if '.sql.gz' in original_name.lower():
            final_filename = f"uploaded_{clean_name}_{timestamp}.sql.gz"
        elif '.gz' in original_name.lower():
            final_filename = f"uploaded_{clean_name}_{timestamp}.gz"
        else:
            final_filename = f"uploaded_{clean_name}_{timestamp}.sql"
        
        # Guardar archivo en el directorio de backups
        backup_dir = backup_manager.backup_dir
        filepath = os.path.join(backup_dir, final_filename)
        
        backup_logger.info(f"Guardando archivo subido: {original_name} -> {final_filename}")
        file.save(filepath)
        
        # Obtener tamaño del archivo
        file_size = os.path.getsize(filepath)
        
        # Crear metadata
        metadata = {
            'original_filename': original_name,
            'created_at': datetime.now().isoformat(),  # Cambiar de upload_timestamp a created_at
            'uploaded_by': current_user.email if hasattr(current_user, 'email') else 'admin',
            'file_size': file_size,
            'type': 'uploaded',
            'description': f'Archivo subido: {original_name}'
        }
        
        # Guardar metadata
        metadata_path = backup_manager.get_metadata_path(final_filename)
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        backup_logger.info(f"Backup subido exitosamente: {final_filename} ({file_size} bytes)")
        
        return jsonify({
            'success': True,
            'message': f'Backup subido exitosamente: {final_filename}',
            'filename': final_filename,
            'original_filename': original_name,
            'size': file_size
        })
        
    except Exception as e:
        backup_logger.error(f"Error en upload_backup endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al subir backup: {str(e)}'
        }), 500


@admin_bp.route('/backup/check-status', methods=['GET'])
@login_required
def check_backup_status():
    """Verificar el estado de la base de datos después de una restauración"""
    try:
        backup_logger.info("Verificando estado de la base de datos")
        
        from app.models import Trabajador, Requerimiento
        
        # Contar registros en las tablas principales
        trabajadores_count = Trabajador.query.count()
        requerimientos_count = Requerimiento.query.count()
        
        backup_logger.info(f"Estado DB: {trabajadores_count} trabajadores, {requerimientos_count} requerimientos")
        
        return jsonify({
            'success': True,
            'trabajadores': trabajadores_count,
            'requerimientos': requerimientos_count,
            'has_data': trabajadores_count > 0 or requerimientos_count > 0,
            'message': f'Base de datos contiene {trabajadores_count} usuarios y {requerimientos_count} requerimientos'
        })
        
    except Exception as e:
        backup_logger.error(f"Error verificando estado de DB: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al verificar estado: {str(e)}'
        }), 500