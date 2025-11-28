import requests
import json

def test_apis():
    try:
        print("📊 Probando APIs de proyectos...")
        
        # API Original (filtrada)
        response1 = requests.get('http://localhost:5050/proyectos_por_trabajador/1', timeout=5)
        print(f'\n📋 API Original (filtrada) - Status: {response1.status_code}')
        if response1.status_code == 200:
            data1 = response1.json()
            print(f'   Proyectos encontrados: {len(data1.get("proyectos", []))}')
            print(f'   Trabajador: {data1.get("trabajador", {}).get("nombre", "N/A")}')
        
        # Nueva API (completa)
        response2 = requests.get('http://localhost:5050/proyectos_por_trabajador_all/1', timeout=5) 
        print(f'\n📋 Nueva API (completa) - Status: {response2.status_code}')
        if response2.status_code == 200:
            data2 = response2.json()
            print(f'   Proyectos encontrados: {len(data2.get("proyectos", []))}')
            print(f'   Trabajador: {data2.get("trabajador", {}).get("nombre", "N/A")}')
            
            # Mostrar diferencias
            if response1.status_code == 200 and response2.status_code == 200:
                diff = len(data2.get("proyectos", [])) - len(data1.get("proyectos", []))
                print(f'\n📈 Diferencia: {diff} proyectos adicionales en la vista completa')
        
        print('\n✅ Prueba de APIs completada')
        
    except requests.exceptions.ConnectionError:
        print('⚠️  Aplicación no está ejecutándose en localhost:5050')
        print('   Para probar las APIs, ejecute: python app.py')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    test_apis()
