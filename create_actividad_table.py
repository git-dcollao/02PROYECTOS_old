"""
Script para crear la tabla actividad_proyecto manualmente
"""

CREATE_TABLE_SQL = """
CREATE TABLE actividad_proyecto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    requerimiento_id INT NOT NULL,
    edt VARCHAR(50) NOT NULL,
    nombre_tarea VARCHAR(500) NOT NULL,
    nivel_esquema INT NOT NULL DEFAULT 1,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    duracion INT NOT NULL,
    dias_corridos INT NULL,
    predecesoras TEXT NULL,
    recursos TEXT NULL,
    progreso DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    datos_adicionales JSON NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (requerimiento_id) REFERENCES requerimiento(id) ON DELETE CASCADE,
    UNIQUE KEY uq_actividad_proyecto_edt (requerimiento_id, edt),
    INDEX idx_actividad_proyecto_requerimiento (requerimiento_id),
    INDEX idx_actividad_proyecto_fecha_inicio (fecha_inicio),
    INDEX idx_actividad_proyecto_fecha_fin (fecha_fin)
);
"""

if __name__ == "__main__":
    print("SQL para crear la tabla actividad_proyecto:")
    print(CREATE_TABLE_SQL)
