📊 **Sistema de Cálculo de Porcentaje de Avance**
El sistema calcula el progreso de las actividades en dos momentos clave y utiliza dos campos diferentes en la tabla actividad_proyecto:
------------------------------------------------------------------------------
🎯 **Campos de Progreso en ActividadProyecto**
**progreso** (Decimal 5,2): Porcentaje calculado automáticamente en base al avance reportado por trabajadores
**porcentaje_avance_validado** (Decimal 5,2): Porcentaje validado oficialmente por supervisores
------------------------------------------------------------------------------
📝** MOMENTO 1: Cuando el Trabajador Guarda Avances**
Ruta: [POST /guardar_avances_trabajador](c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\controllers_main.py#L4389-L4600)

Proceso paso a paso:
1. El trabajador reporta su avance personal en la interfaz de [avance-actividades.html](c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\templates\avance-actividades.html)

2. Se actualiza la tabla avance_actividad:
    * progreso_anterior = progreso actual anterior
    * progreso_actual = nuevo progreso reportado
    * Se guarda la fecha de actualización
3. Se crea un registro en historial_avance_actividad:
    ```python
        historial_entry = HistorialAvanceActividad(
        requerimiento_id=proyecto_id,
        trabajador_id=trabajador_id,
        actividad_id=actividad.id,
        progreso_anterior=progreso_real_anterior,
        progreso_nuevo=progreso_nuevo,
        diferencia=progreso_nuevo - progreso_real_anterior,
        comentarios=comentarios_generales,
        fecha_cambio=datetime.now(),
        sesion_guardado=sesion_guardado,  # UUID único para agrupar cambios
        validado=False  # ⚠️ Importante: Inicia como NO VALIDADO
    )
    ```
4. Se calcula el progreso total de la actividad usando [calcular_progreso_actividad()](c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\controllers_main.py#L4176-L4256):
    ```python
        def calcular_progreso_actividad(actividad_id):
        """
        Calcula progreso basado en TODOS los trabajadores asignados

        Fórmula:
        - horas_por_dia_trabajador = (porcentaje_asignacion * 8 horas) / 100
        - horas_totales_trabajador = horas_por_dia * duracion_actividad
        - horas_completadas_trabajador = horas_totales * (progreso_actual / 100)

        progreso_total = (suma_horas_completadas / suma_horas_totales) * 100
        """
    ```
 las 8 horas es el promedio diario de trabajo en funcion del trabajo semanal que debe realizar el trabajador 
    EJ: (40/5 de lunes a viernes = 8 hrs diarias) 

Ejemplo práctico:
    * Actividad de 10 días
    * Trabajador 1: Asignado al 50%, reporta 40% de avance
        * Horas/día: (50% × 8h) / 100 = 4h
        * Horas totales: 4h × 10 días = 40h
        * Horas completadas: 40h × 40% = 16h
    * Trabajador 2: Asignado al 100%, reporta 60% de avance
        * Horas/día: (100% × 8h) / 100 = 8h
        * Horas totales: 8h × 10 días = 80h
        * Horas completadas: 80h × 60% = 48h
    * Progreso Total: (16h + 48h) / (40h + 80h) × 100 = 53.33%

5. Se actualiza el campo progreso en actividad_proyecto:
    ```python
        actividad.progreso = progreso_actividad_calculado
        actividad.fecha_actualizacion = datetime.now()
    ```
6. ⚠️ IMPORTANTE: En este momento NO se recalcula la jerarquía de actividades padre. El sistema espera la validación del supervisor.

================================================================================
✅ MOMENTO 2: Cuando el Supervisor Valida el Avance
Ruta: [POST /validar-avances/validar](c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\controllers\validar_avances_controller.py#L212-L282)

Proceso de validación:
1. El supervisor accede a [/validar-avances](c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\templates\validar-avances.html)

2. Puede realizar tres acciones:
    * ✅ Aprobar: Acepta el porcentaje reportado
    * ✏️ Corregir: Modifica el porcentaje antes de validar
    * ❌ Rechazar: Rechaza el reporte con comentarios
3. Al validar (aprobar o corregir):
    ```python
        # Actualizar historial
        historial.validado = True
        historial.validado_por_id = current_user.id
        historial.fecha_validacion = datetime.utcnow()
        historial.comentario_validacion = comentario

        # Actualizar porcentaje validado oficial
        actividad.porcentaje_avance_validado = historial.progreso_nuevo
    ```

4. 🌳 AQUÍ VIENE EL CÁLCULO JERÁRQUICO:
    Se recalcula el progreso nuevamente y se propaga hacia arriba en la jerarquía EDT:
    ```python
        # 1. Recalcular progreso de la actividad
        progreso_calculado = calcular_progreso_actividad(actividad.id)
        actividad.progreso = progreso_calculado

        # 2. Propagar cambios a actividades padre
        recalcular_padres_recursivo(actividad.edt, requerimiento_id)
    ```


5. La función [recalcular_padres_recursivo()](c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\controllers_main.py#L4308-L4380) hace lo siguiente:
    * Toma el EDT de la actividad hija (ej: 1.1.2.3)
    * Navega hacia arriba: 1.1.2 → 1.1 → 1
    * Para cada padre, usa [calcular_progreso_jerarquico()](c:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS\app\controllers_main.py#L4259-L4306):
    ```python
        def calcular_progreso_jerarquico(actividad_id):
        """
        - Si la actividad tiene hijas: promedio ponderado por duración
        - Si es una hoja (sin hijas): usa calcular_progreso_actividad()
        """

        # Buscar hijas directas (1.1 → 1.1.1, 1.1.2, pero NO 1.1.1.1)
        hijas = ActividadProyecto.query.filter(
            ActividadProyecto.edt.like(f"{actividad.edt}.%"),
            ~ActividadProyecto.edt.like(f"{actividad.edt}.%.%")
        ).all()

        if not hijas:
            # Es hoja - calcular por trabajadores
            return calcular_progreso_actividad(actividad_id)

        # Es padre - promedio ponderado
        total_peso = sum(hija.duracion for hija in hijas)
        progreso_ponderado = sum(
            (hija.progreso * hija.duracion) / total_peso 
            for hija in hijas
        )
        return progreso_ponderado
    ```


Ejemplo de jerarquía:
    1 (Proyecto completo)
    ├─ 1.1 (Diseño) - 30 días
    │  ├─ 1.1.1 (Planos) - 10 días - 70% completado
    │  └─ 1.1.2 (Maquetas) - 20 días - 40% completado
    └─ 1.2 (Construcción) - 50 días - 20% completado

    Cálculo de 1.1:
    progreso_1.1 = (70% × 10 + 40% × 20) / (10 + 20) 
                 = (700 + 800) / 30 
                 = 50%

    Cálculo de 1:
    progreso_1 = (50% × 30 + 20% × 50) / (30 + 50)
               = (1500 + 1000) / 80
               = 31.25%

📊 Diferencias entre progreso y porcentaje_avance_validado
    | Campo | Cuándo se actualiza | Quién lo controla | Propósito |
    |---|---|---|---|
    | progreso      | • Al guardar avances trabajador<br>• Al validar supervisor<br>• En recálculos jerárquicos | Sistema (cálculo automático) |    Refleja el estado actual calculado en tiempo real |
    | porcentaje_avance_validado | Solo al validar/corregir supervisor | Supervisor | Representa el avance oficialmente aprobado |

🔄 Flujo Completo Visual
    👷 TRABAJADOR REPORTA 60% EN ACTIVIDAD 1.1.1
        ↓
    📝 Actualiza tabla avance_actividad
        progreso_actual = 60%
        ↓
    🧮 Calcula progreso total actividad
        calcular_progreso_actividad() → 53%
        ↓
    💾 Actualiza actividad.progreso = 53%
        ↓
    📋 Crea historial (validado=False)
        ↓
    ⏸️ ESPERA VALIDACIÓN (NO recalcula padres aún)

    ---

    👨‍💼 SUPERVISOR VALIDA
        ↓
    ✅ Marca historial.validado = True
        ↓
    💾 Actualiza actividad.porcentaje_avance_validado = 53%
        ↓
    🌳 RECALCULA JERARQUÍA
        ├─ Recalcula progreso de 1.1.1 → 53%
        ├─ Recalcula padre 1.1 (promedio ponderado hijas) → 45%
        └─ Recalcula raíz 1 (promedio ponderado hijas) → 35%


🎯 Resumen Ejecutivo
¿Cuándo se calculan los porcentajes?
    1. Inmediatamente cuando el trabajador guarda → actualiza progreso
    2. Al validar el supervisor → actualiza porcentaje_avance_validado y recalcula jerarquía

¿Cómo se calculan?
    * Actividades hoja (con trabajadores): Suma ponderada por horas asignadas
    * Actividades padre: Promedio ponderado por duración de hijas

¿Por qué dos campos?
    * progreso: Vista "en vivo" del estado actual
    * porcentaje_avance_validado: Fuente de verdad oficial aprobada por autoridad
