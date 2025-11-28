"""
Script de Configuración Integral
Configuración y inicialización de todos los sistemas de mejora
"""
import os
import sys
from pathlib import Path

def create_production_config():
    """Crear configuración de producción robusta"""
    config_content = '''"""
Configuración de Producción con Mejoras Implementadas
"""
import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'production-secret-key-change-this'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'
    
    # Cache
    CACHE_TYPE = 'redis'
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'flask_app'
    
    # Database
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # File Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls'}
    
    # Performance
    JSONIFY_PRETTYPRINT_REGULAR = False
    
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql://user:password@localhost:3308/database'
    LOG_LEVEL = 'DEBUG'
    SESSION_COOKIE_SECURE = False
    
class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'ERROR'
    CACHE_TYPE = 'simple'
    
class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL_PROD')
    LOG_LEVEL = 'WARNING'
    
    # Production security
    FORCE_HTTPS = True
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}'''
    
    with open('config_enhanced.py', 'w') as f:
        f.write(config_content)
    
    print("✅ Enhanced config created: config_enhanced.py")

def create_enhanced_requirements():
    """Agregar nuevas dependencias al requirements.txt"""
    new_packages = [
        "# Performance and Caching",
        "redis==5.0.1",
        "Flask-Caching==2.1.0",
        "",
        "# Validation and Security", 
        "bleach==6.1.0",
        "python-decouple==3.8",
        "",
        "# Testing Enhanced",
        "pytest-mock==3.12.0",
        "pytest-xdist==3.5.0",
        "factory-boy==3.3.0",
        "",
        "# Monitoring and Logging",
        "structlog==23.2.0",
        "python-json-logger==2.0.7",
        "",
        "# Development Tools",
        "pre-commit==3.6.0",
        "bandit==1.7.5",
        "safety==2.3.5"
    ]
    
    # Leer requirements actual
    try:
        with open('requirements.txt', 'r') as f:
            current_content = f.read()
    except FileNotFoundError:
        current_content = ""
    
    # Agregar nuevos paquetes
    enhanced_content = current_content + "\n\n" + "\n".join(new_packages)
    
    with open('requirements_enhanced.txt', 'w') as f:
        f.write(enhanced_content)
    
    print("✅ Enhanced requirements created: requirements_enhanced.txt")

def create_makefile():
    """Crear Makefile para comandos comunes"""
    makefile_content = '''# Makefile para Proyecto Flask con Mejoras

.PHONY: help install test lint format security clean dev prod backup

help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

install: ## Instalar dependencias
	pip install -r requirements_enhanced.txt
	pre-commit install

test: ## Ejecutar todos los tests
	python run_tests.py

test-coverage: ## Ejecutar tests con coverage
	python run_tests.py --coverage --html-report

test-fast: ## Ejecutar tests en paralelo
	python -m pytest tests/ -n auto -v

lint: ## Verificar código con linting
	flake8 app/ tests/
	bandit -r app/

format: ## Formatear código
	black app/ tests/
	isort app/ tests/

security: ## Verificar seguridad
	bandit -r app/
	safety check

clean: ## Limpiar archivos temporales
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage

dev: ## Ejecutar en modo desarrollo
	flask --app app run --debug --port 5050

prod: ## Ejecutar en modo producción
	gunicorn -w 4 -b 0.0.0.0:5050 "app:create_app()"

docker-dev: ## Ejecutar con Docker (desarrollo)
	docker-compose up --build

docker-prod: ## Ejecutar con Docker (producción)
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

backup: ## Crear backup de base de datos
	flask db-backup

integrity: ## Verificar integridad de BD
	flask db-integrity

migrate: ## Crear nueva migración
	flask db migrate -m "$(MESSAGE)"

upgrade: ## Aplicar migraciones
	flask db upgrade

init-db: ## Inicializar base de datos
	flask db init
	flask db migrate -m "Initial migration"
	flask db upgrade

logs: ## Ver logs en tiempo real
	tail -f logs/app.log

stats: ## Ver estadísticas de cache
	curl http://localhost:5050/admin/cache-stats

setup: install init-db ## Configuración inicial completa
	@echo "✅ Proyecto configurado correctamente"
	@echo "Ejecuta 'make dev' para iniciar el servidor de desarrollo"'''
    
    with open('Makefile', 'w') as f:
        f.write(makefile_content)
    
    print("✅ Makefile created")

def create_pre_commit_config():
    """Crear configuración de pre-commit hooks"""
    precommit_content = '''repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-toml
      - id: check-xml
      - id: check-merge-conflict
      - id: debug-statements
      - id: check-docstring-first

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, app/]
        exclude: tests/

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python run_tests.py
        language: python
        pass_filenames: false
        always_run: true'''
    
    with open('.pre-commit-config.yaml', 'w') as f:
        f.write(precommit_content)
    
    print("✅ Pre-commit config created: .pre-commit-config.yaml")

def create_docker_compose_production():
    """Crear configuración Docker para producción"""
    docker_prod_content = '''# docker-compose.prod.yml
version: '3.8'

services:
  proyectos_app:
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - proyectos_app
    restart: unless-stopped

volumes:
  redis_data:'''
    
    with open('docker-compose.prod.yml', 'w') as f:
        f.write(docker_prod_content)
    
    print("✅ Docker production config created: docker-compose.prod.yml")

def create_github_workflows():
    """Crear workflows de GitHub Actions"""
    os.makedirs('.github/workflows', exist_ok=True)
    
    ci_workflow = '''name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: testpassword
          MYSQL_DATABASE: testdb
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements_enhanced.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements_enhanced.txt
    
    - name: Lint with flake8
      run: |
        flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 app/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Security check with bandit
      run: bandit -r app/
    
    - name: Test with pytest
      env:
        DATABASE_URL: mysql://root:testpassword@localhost:3306/testdb
        REDIS_URL: redis://localhost:6379/0
        FLASK_ENV: testing
      run: |
        python run_tests.py --coverage
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Run Snyk to check for vulnerabilities
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}'''
    
    with open('.github/workflows/ci.yml', 'w') as f:
        f.write(ci_workflow)
    
    print("✅ GitHub Actions workflow created: .github/workflows/ci.yml")

def main():
    """Función principal de configuración"""
    print("🚀 CONFIGURACIÓN INTEGRAL DE MEJORAS")
    print("=" * 50)
    
    # Crear todos los archivos de configuración
    create_production_config()
    create_enhanced_requirements()
    create_makefile()
    create_pre_commit_config()
    create_docker_compose_production()
    create_github_workflows()
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 50)
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Instalar dependencias: make install")
    print("2. Configurar base de datos: make init-db")
    print("3. Ejecutar tests: make test")
    print("4. Iniciar desarrollo: make dev")
    print("\n💡 COMANDOS ÚTILES:")
    print("• make help - Ver todos los comandos disponibles")
    print("• make test-coverage - Tests con reporte de cobertura")
    print("• make security - Verificar seguridad del código")
    print("• make backup - Crear backup de base de datos")

if __name__ == "__main__":
    main()