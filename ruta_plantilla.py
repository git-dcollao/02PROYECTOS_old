# Ruta para descargar plantilla de ejemplo
@controllers_bp.route('/descargar-plantilla-gantt', methods=['GET'], endpoint='descargar_plantilla_gantt')
def descargar_plantilla_gantt():
    """Descargar plantilla de ejemplo para archivos Gantt"""
    try:
        import pandas as pd
        from flask import send_file
        import tempfile
        import os
        
        # Datos de ejemplo
        datos_ejemplo = {
            'Id': [1, 2, 3, 4, 5, 6, 7],
            'Nivel de esquema': [1, 2, 3, 3, 2, 3, 3],
            'EDT': ['1', '1.1', '1.1.1', '1.1.2', '1.2', '1.2.1', '1.2.2'],
            'Nombre de tarea': [
                'Proyecto Ejemplo',
                'Fase de Planificación',
                'Análisis de Requerimientos',
                'Diseño del Sistema',
                'Fase de Desarrollo',
                'Desarrollo Frontend',
                'Desarrollo Backend'
            ],
            'Duración': [100, 30, 10, 20, 70, 35, 35],
            'Comienzo': [
                '2025-01-01',
                '2025-01-01',
                '2025-01-01',
                '2025-01-11',
                '2025-01-31',
                '2025-01-31',
                '2025-02-15'
            ],
            'Fin': [
                '2025-04-30',
                '2025-01-30',
                '2025-01-10',
                '2025-01-30',
                '2025-04-30',
                '2025-02-14',
                '2025-04-30'
            ],
            'Predecesoras': ['', '', '', '3', '2', '4', '6'],
            'Nombres de los recursos': [
                'Equipo Completo',
                'Analista Senior',
                'Analista de Sistemas',
                'Arquitecto de Software',
                'Equipo Desarrollo',
                'Desarrollador Frontend',
                'Desarrollador Backend'
            ]
        }
        
        # Crear DataFrame
        df = pd.DataFrame(datos_ejemplo)
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            df.to_excel(tmp_file.name, index=False)
            
            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name='plantilla_proyecto_gantt_ejemplo.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    except Exception as e:
        flash(f'Error al generar plantilla: {str(e)}', 'error')
        return redirect(url_for('controllers.ruta_proyecto_llenar'))
