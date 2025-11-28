import requests

try:
    with open('plantilla_proyecto_gantt.xlsx', 'rb') as f:
        files = {'archivo': ('plantilla_proyecto_gantt.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post('http://127.0.0.1:5050/procesar-proyecto-xlsx', files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            proyectos = data.get('proyectos_para_asignar', [])
            print(f"Proyectos detectados: {len(proyectos)}")
            
            for i, p in enumerate(proyectos, 1):
                print(f"  {i}. {p.get('nombre_tarea', 'N/A')}")
                
            print(f"\nTodos los datos: {data}")
        else:
            print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
