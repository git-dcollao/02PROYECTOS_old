backup_path = r"backups\BACKUP_FINAL_LIMPIO_20251103_111639.sql"

print("🔍 Diagnosticando archivo de backup...\n")

# Probar diferentes encodings
encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

for enc in encodings:
    try:
        print(f"📝 Probando encoding: {enc}")
        with open(backup_path, 'r', encoding=enc, errors='ignore') as f:
            line_count = 0
            found_pages = False
            
            for line_num, line in enumerate(f, 1):
                line_count += 1
                if line_count > 1000:  # Solo primeras 1000 líneas
                    break
                
                if "pages" in line.lower() and "insert" in line.lower():
                    print(f"   ✅ Línea {line_num}: {line[:80]}...")
                    found_pages = True
            
            if not found_pages:
                print(f"   ❌ No se encontró INSERT de pages en las primeras 1000 líneas")
        
        print()
    
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
