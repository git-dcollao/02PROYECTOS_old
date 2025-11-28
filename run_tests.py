"""
Script para ejecutar tests y generar reportes
Usage: python run_tests.py [--coverage] [--html-report] [--specific-test test_name]
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Ejecutar comando y manejar errores"""
    print(f"\n🔍 {description}")
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} - ÉXITO")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERROR")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ {description} - COMANDO NO ENCONTRADO")
        print("Asegúrate de que pytest esté instalado: pip install pytest")
        return False

def main():
    """Función principal para ejecutar tests"""
    print("🧪 SISTEMA DE TESTING - PROYECTO FLASK")
    print("=" * 50)
    
    # Verificar estructura de directorios
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("❌ Directorio 'tests' no encontrado")
        print("Creando estructura de testing...")
        tests_dir.mkdir(exist_ok=True)
        return False
    
    # Comando base de pytest
    base_cmd = ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    # Argumentos desde línea de comandos  
    if "--coverage" in sys.argv:
        base_cmd.extend(["--cov=app", "--cov-report=term-missing"])
        if "--html-report" in sys.argv:
            base_cmd.extend(["--cov-report=html:htmlcov"])
    
    if "--specific-test" in sys.argv:
        try:
            test_index = sys.argv.index("--specific-test") + 1
            test_name = sys.argv[test_index]
            base_cmd.append(f"-k {test_name}")
        except (IndexError, ValueError):
            print("❌ Error: --specific-test requiere especificar el nombre del test")
            return False
    
    # Ejecutar tests
    success = run_command(base_cmd, "Ejecutando Suite de Tests")
    
    if success:
        print("\n🎉 TESTS COMPLETADOS EXITOSAMENTE")
        
        if "--coverage" in sys.argv:
            print("\n📊 REPORTE DE COBERTURA GENERADO")
            if "--html-report" in sys.argv:
                print("📄 Reporte HTML disponible en: htmlcov/index.html")
    else:
        print("\n💥 ALGUNOS TESTS FALLARON")
        print("Revisa los errores arriba y corrige los problemas")
    
    return success

if __name__ == "__main__":
    # Configurar entorno de testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['TESTING'] = 'true'
    
    # Información de uso
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print(__doc__)
        sys.exit(0)
    
    # Ejecutar tests
    success = main()
    sys.exit(0 if success else 1)