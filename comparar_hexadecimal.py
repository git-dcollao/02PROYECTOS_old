import pandas as pd

# Leer el archivo Excel
df = pd.read_excel("DOCS/Tip/all.xlsx")

# Filtrar solo nivel de esquema = 1 
nivel_1 = df[df['Nivel de esquema'] == 1]

print("=== COMPARACIÓN HEXADECIMAL ===")
for index, row in nivel_1.iterrows():
    nombre = str(row['Nombre de tarea'])
    hex_value = nombre.encode('utf-8').hex().upper()
    print(f"Nombre: '{nombre}'")
    print(f"Hex: {hex_value}")
    print(f"Length: {len(nombre)}")
    print("---")
    
# Comparar específicamente con lo que está en la BD
nombre_bd = "   PROYECTO B"
hex_bd = "20202050524F594543544F2042"

print(f"\n=== COMPARACIÓN CON BD ===")
print(f"BD Nombre: '{nombre_bd}'")
print(f"BD Hex: {hex_bd}")

# Buscar coincidencias
for index, row in nivel_1.iterrows():
    nombre = str(row['Nombre de tarea'])
    hex_value = nombre.encode('utf-8').hex().upper()
    if hex_value == hex_bd:
        print(f"¡COINCIDENCIA ENCONTRADA!: '{nombre}'")
        break
else:
    print("❌ No se encontró coincidencia exacta")
    print("\nPrimera diferencia encontrada:")
    for index, row in nivel_1.iterrows():
        nombre = str(row['Nombre de tarea'])
        if "PROYECTO B" in nombre:
            hex_value = nombre.encode('utf-8').hex().upper()
            print(f"Archivo: '{nombre}' -> {hex_value}")
            print(f"BD:      '{nombre_bd}' -> {hex_bd}")
            
            # Comparar carácter por carácter
            min_len = min(len(hex_value), len(hex_bd))
            for i in range(0, min_len, 2):
                if hex_value[i:i+2] != hex_bd[i:i+2]:
                    char_archivo = bytes.fromhex(hex_value[i:i+2]).decode('utf-8')
                    char_bd = bytes.fromhex(hex_bd[i:i+2]).decode('utf-8')
                    print(f"Diferencia en posición {i//2}: archivo='{char_archivo}' vs bd='{char_bd}'")
                    break
            break
