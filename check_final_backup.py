import gzip
import re
import os

backup_dir = r"C:\Users\Daniel Collao\Documents\Repositories\02PROYECTOS - Final Backup\backups"

print("🔍 Buscando backups con 42 páginas...\n")

for filename in os.listdir(backup_dir):
    if filename.endswith('.sql.gz') or filename.endswith('.sql'):
        filepath = os.path.join(backup_dir, filename)
        
        try:
            if filename.endswith('.gz'):
                with gzip.open(filepath, 'rt', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # Buscar INSERT de páginas
            match = re.search(r'INSERT INTO `?pages`? VALUES(.+?);', content, re.DOTALL)
            
            if match:
                pages_count = len(match.group(1).split('),('))
                print(f"📄 {filename:<50} → {pages_count} páginas")
                
                if pages_count == 42:
                    print(f"   ✅ Este backup tiene las 42 páginas!")
                    print(f"   📂 Ruta: {filepath}")
            else:
                print(f"❌ {filename:<50} → Sin datos de páginas")
        
        except Exception as e:
            print(f"⚠️  {filename:<50} → Error: {str(e)[:50]}")

print("\n" + "="*80)
