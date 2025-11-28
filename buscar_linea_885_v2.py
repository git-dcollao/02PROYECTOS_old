backup_path = r"backups\BACKUP_FINAL_LIMPIO_20251103_111639.sql"

print("🔍 Buscando INSERT de pages alrededor de la línea 885...\n")

with open(backup_path, 'r', encoding='latin-1') as f:
    lines = f.readlines()
    
    total_lines = len(lines)
    print(f"Total de líneas en el archivo: {total_lines}\n")
    
    # Buscar alrededor de la línea 885
    start = max(0, 880)
    end = min(total_lines, 890)
    
    for i in range(start, end):
        line = lines[i]
        line_num = i + 1
        
        if len(line) > 100:
            preview = line[:100] + f"... (total: {len(line)} caracteres)"
        else:
            preview = line.strip()
        
        marker = "🔍" if "INSERT" in line and "pages" in line else "   "
        print(f"{marker} Línea {line_num}: {preview}")
        
        if "INSERT" in line and "pages" in line:
            print(f"\n✅ ¡ENCONTRADA! Línea {line_num}")
            print(f"   Longitud: {len(line)} caracteres")
            print(f"   Inicio: {line[:150]}")
            
            # Intentar contar páginas
            if "VALUES (" in line:
                start_idx = line.find("VALUES (")
                if start_idx != -1:
                    data = line[start_idx + 8:]
                    count = data.count('),(') + 1
                    print(f"   📊 Páginas estimadas: {count}")
            
            # Guardar la línea para importación
            with open("backups/insert_pages_line.sql", 'w', encoding='utf-8') as out:
                out.write(line)
            print(f"\n💾 Línea guardada en backups/insert_pages_line.sql")
