"""
Sistema de Migración y Versionado de Base de Datos Avanzado
Herramientas para gestionar cambios de esquema de forma segura
"""
import os
import json
import shutil
from datetime import datetime
from flask import current_app
from flask_migrate import Migrate
from alembic import command, script
from alembic.config import Config
import logging

logger = logging.getLogger(__name__)

class DatabaseMigrationManager:
    """Gestor avanzado de migraciones de base de datos"""
    
    def __init__(self, app=None, db=None):
        self.app = app
        self.db = db
        self.migrate = None
        
        if app and db:
            self.init_app(app, db)
    
    def init_app(self, app, db):
        """Inicializar el gestor con la app Flask"""
        self.app = app
        self.db = db
        self.migrate = Migrate(app, db)
        
        # Configurar directorio de migraciones
        migrations_dir = os.path.join(app.root_path, '..', 'migrations')
        app.config.setdefault('MIGRATIONS_DIR', migrations_dir)
        
        # Crear estructura de directorios
        self._ensure_migration_structure()
    
    def _ensure_migration_structure(self):
        """Crear estructura de directorios para migraciones"""
        base_dir = self.app.config['MIGRATIONS_DIR']
        
        directories = [
            base_dir,
            os.path.join(base_dir, 'versions'),
            os.path.join(base_dir, 'backups'),
            os.path.join(base_dir, 'seeds'),
            os.path.join(base_dir, 'rollback_scripts')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def create_backup(self, backup_name=None):
        """Crear backup de la base de datos antes de migración"""
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
        
        backup_dir = os.path.join(self.app.config['MIGRATIONS_DIR'], 'backups')
        backup_path = os.path.join(backup_dir, f"{backup_name}.sql")
        
        try:
            # Para MySQL
            if 'mysql' in self.app.config['SQLALCHEMY_DATABASE_URI']:
                import subprocess
                
                # Extraer parámetros de conexión
                db_uri = self.app.config['SQLALCHEMY_DATABASE_URI']
                # mysql://user:password@host:port/database
                parts = db_uri.replace('mysql://', '').split('@')
                user_pass = parts[0].split(':')
                host_port_db = parts[1].split('/')
                
                user = user_pass[0]
                password = user_pass[1] if len(user_pass) > 1 else ''
                host_port = host_port_db[0].split(':')
                host = host_port[0]
                port = host_port[1] if len(host_port) > 1 else '3306'
                database = host_port_db[1]
                
                # Comando mysqldump
                cmd = [
                    'mysqldump',
                    f'--host={host}',
                    f'--port={port}',
                    f'--user={user}',
                    f'--password={password}',
                    '--single-transaction',
                    '--routines',
                    '--triggers',
                    database
                ]
                
                with open(backup_path, 'w') as backup_file:
                    subprocess.run(cmd, stdout=backup_file, check=True)
                
                logger.info(f"Database backup created: {backup_path}")
                return backup_path
                
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return None
    
    def create_migration(self, message, auto=True):
        """Crear nueva migración con validaciones"""
        try:
            # Crear backup antes de generar migración
            backup_path = self.create_backup()
            
            # Generar migración
            if auto:
                command_result = self._run_alembic_command('revision', '--autogenerate', '-m', message)
            else:
                command_result = self._run_alembic_command('revision', '-m', message)
            
            # Registrar en log de migraciones
            self._log_migration_action('create', message, backup_path)
            
            logger.info(f"Migration created successfully: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
            return False
    
    def apply_migration(self, revision='head'):
        """Aplicar migración con validaciones y rollback automático"""
        try:
            # Crear backup antes de aplicar
            backup_path = self.create_backup()
            
            # Obtener revisión actual
            current_revision = self.get_current_revision()
            
            # Aplicar migración
            self._run_alembic_command('upgrade', revision)
            
            # Verificar que la migración se aplicó correctamente
            if self._verify_migration_success():
                self._log_migration_action('apply', revision, backup_path, current_revision)
                logger.info(f"Migration applied successfully: {revision}")
                return True
            else:
                # Rollback automático si falla la verificación
                logger.error("Migration verification failed, rolling back...")
                self.rollback_migration(current_revision)
                return False
                
        except Exception as e:
            logger.error(f"Error applying migration: {e}")
            # Intentar rollback automático
            try:
                if current_revision:
                    self.rollback_migration(current_revision)
            except:
                pass
            return False
    
    def rollback_migration(self, target_revision):
        """Hacer rollback a una revisión específica"""
        try:
            backup_path = self.create_backup()
            current_revision = self.get_current_revision()
            
            self._run_alembic_command('downgrade', target_revision)
            
            self._log_migration_action('rollback', target_revision, backup_path, current_revision)
            logger.info(f"Rollback completed to revision: {target_revision}")
            return True
            
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False
    
    def get_current_revision(self):
        """Obtener revisión actual de la base de datos"""
        try:
            alembic_cfg = self._get_alembic_config()
            script_dir = script.ScriptDirectory.from_config(alembic_cfg)
            
            with self.app.app_context():
                from alembic import context
                with self.db.engine.connect() as connection:
                    context.configure(connection=connection)
                    return context.get_current_revision()
                    
        except Exception as e:
            logger.error(f"Error getting current revision: {e}")
            return None
    
    def get_migration_history(self):
        """Obtener historial de migraciones"""
        try:
            log_path = os.path.join(self.app.config['MIGRATIONS_DIR'], 'migration_log.json')
            
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            logger.error(f"Error reading migration history: {e}")
            return []
    
    def validate_schema_integrity(self):
        """Validar integridad del esquema de base de datos"""
        try:
            integrity_checks = []
            
            with self.app.app_context():
                # Verificar tablas principales
                tables_to_check = [
                    'user', 'requerimiento', 'trabajador', 'recinto',
                    'custom_role', 'user_page_permission'
                ]
                
                for table in tables_to_check:
                    if self.db.engine.has_table(table):
                        integrity_checks.append({
                            'table': table,
                            'exists': True,
                            'status': 'OK'
                        })
                    else:
                        integrity_checks.append({
                            'table': table,
                            'exists': False,
                            'status': 'MISSING'
                        })
                
                # Verificar constrainst de FK
                result = self.db.engine.execute("""
                    SELECT CONSTRAINT_NAME, TABLE_NAME 
                    FROM information_schema.TABLE_CONSTRAINTS 
                    WHERE CONSTRAINT_TYPE = 'FOREIGN KEY'
                """)
                
                fk_count = len(list(result))
                integrity_checks.append({
                    'check': 'foreign_keys',
                    'count': fk_count,
                    'status': 'OK' if fk_count > 0 else 'WARNING'
                })
            
            return integrity_checks
            
        except Exception as e:
            logger.error(f"Error validating schema integrity: {e}")
            return []
    
    def create_seed_file(self, name, data):
        """Crear archivo de seed data"""
        try:
            seeds_dir = os.path.join(self.app.config['MIGRATIONS_DIR'], 'seeds')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            seed_file = os.path.join(seeds_dir, f"{timestamp}_{name}.json")
            
            with open(seed_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Seed file created: {seed_file}")
            return seed_file
            
        except Exception as e:
            logger.error(f"Error creating seed file: {e}")
            return None
    
    def _run_alembic_command(self, *args):
        """Ejecutar comando de Alembic"""
        alembic_cfg = self._get_alembic_config()
        return command.main(alembic_cfg, *args)
    
    def _get_alembic_config(self):
        """Obtener configuración de Alembic"""
        migrations_dir = self.app.config['MIGRATIONS_DIR']
        alembic_cfg = Config(os.path.join(migrations_dir, 'alembic.ini'))
        alembic_cfg.set_main_option('script_location', migrations_dir)
        return alembic_cfg
    
    def _verify_migration_success(self):
        """Verificar que la migración se aplicó correctamente"""
        try:
            # Ejecutar validaciones básicas
            integrity_checks = self.validate_schema_integrity()
            
            # Verificar que no hay errores críticos
            for check in integrity_checks:
                if check.get('status') == 'MISSING':
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying migration: {e}")
            return False
    
    def _log_migration_action(self, action, target, backup_path=None, from_revision=None):
        """Registrar acción de migración en log"""
        try:
            log_path = os.path.join(self.app.config['MIGRATIONS_DIR'], 'migration_log.json')
            
            # Cargar log existente
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = []
            
            # Agregar nueva entrada
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'target': target,
                'from_revision': from_revision,
                'backup_path': backup_path,
                'user': 'system',  # Mejorar para incluir usuario actual
                'status': 'completed'
            }
            
            log_data.append(log_entry)
            
            # Guardar log
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error logging migration action: {e}")

# CLI Commands para gestión de migraciones
def register_migration_commands(app, db):
    """Registrar comandos CLI para migraciones"""
    migration_manager = DatabaseMigrationManager(app, db)
    
    @app.cli.command()
    def db_backup():
        """Crear backup de la base de datos"""
        backup_path = migration_manager.create_backup()
        if backup_path:
            print(f"✅ Backup created: {backup_path}")
        else:
            print("❌ Error creating backup")
    
    @app.cli.command()
    def db_integrity():
        """Verificar integridad del esquema"""
        checks = migration_manager.validate_schema_integrity()
        
        print("\n🔍 SCHEMA INTEGRITY CHECK")
        print("=" * 50)
        
        for check in checks:
            status_icon = "✅" if check.get('status') == 'OK' else "⚠️" if check.get('status') == 'WARNING' else "❌"
            
            if 'table' in check:
                print(f"{status_icon} Table '{check['table']}': {check['status']}")
            else:
                print(f"{status_icon} {check.get('check', 'Unknown')}: {check.get('status', 'Unknown')}")
    
    @app.cli.command()
    def db_history():
        """Mostrar historial de migraciones"""
        history = migration_manager.get_migration_history()
        
        print("\n📜 MIGRATION HISTORY")
        print("=" * 70)
        
        for entry in history[-10:]:  # Últimas 10
            timestamp = entry.get('timestamp', 'Unknown')
            action = entry.get('action', 'Unknown')
            target = entry.get('target', 'Unknown')
            
            print(f"{timestamp} | {action.upper()} | {target}")
        
        if len(history) > 10:
            print(f"\n... and {len(history) - 10} more entries")

# Instancia global
db_migration_manager = DatabaseMigrationManager()