/**
 * DEBUG SCRIPT - Copiar y pegar en la consola del navegador
 * ===========================================================
 * Ejecutar cuando estés en: http://localhost:5050/admin/backup/v2
 */

console.clear();
console.log('%c🔍 INICIANDO DIAGNÓSTICO BACKUP MANAGER V2', 'background: #0d6efd; color: white; padding: 5px 10px; font-weight: bold;');
console.log('');

// 1. Verificar que backupManager existe
console.log('%c1️⃣ Verificando instancia de BackupManagerV2', 'color: #0d6efd; font-weight: bold;');
if (typeof backupManager === 'undefined') {
    console.error('❌ backupManager NO DEFINIDO');
    console.log('💡 Solución: El script backup-manager-v2.js no se cargó o hay un error de sintaxis');
} else {
    console.log('✅ backupManager existe');
    console.log('   - Tipo:', typeof backupManager);
    console.log('   - Constructor:', backupManager.constructor.name);
    console.log('   - Backups cargados:', backupManager.backups?.length || 0);
    console.log('   - Página actual:', backupManager.currentPage);
}
console.log('');

// 2. Verificar elementos DOM críticos
console.log('%c2️⃣ Verificando elementos DOM', 'color: #0d6efd; font-weight: bold;');
const criticalElements = {
    'btnCreateBackup': 'Botón Crear Backup',
    'btnUploadBackup': 'Botón Subir Backup',
    'btnRefresh': 'Botón Refrescar',
    'backupsList': 'Tbody de la tabla',
    'totalBackups': 'Stat: Total Backups',
    'dbStatus': 'Badge estado BD',
    'formCreateBackup': 'Form crear backup',
    'modalCreateBackup': 'Modal crear backup',
    'modalUploadBackup': 'Modal subir backup',
    'searchBackup': 'Campo búsqueda'
};

let missingElements = 0;
for (const [id, desc] of Object.entries(criticalElements)) {
    const element = document.getElementById(id);
    if (element) {
        console.log(`✅ ${desc} (${id})`);
    } else {
        console.error(`❌ ${desc} (${id}) - NO ENCONTRADO`);
        missingElements++;
    }
}

if (missingElements > 0) {
    console.warn(`⚠️ ${missingElements} elementos faltantes`);
}
console.log('');

// 3. Verificar Bootstrap
console.log('%c3️⃣ Verificando Bootstrap', 'color: #0d6efd; font-weight: bold;');
if (typeof bootstrap === 'undefined') {
    console.error('❌ Bootstrap NO CARGADO');
} else {
    console.log('✅ Bootstrap cargado');
    console.log('   - Versión:', bootstrap.Modal ? 'Modal disponible' : 'Modal NO disponible');
}
console.log('');

// 4. Test de API endpoints
console.log('%c4️⃣ Testing API endpoints', 'color: #0d6efd; font-weight: bold;');

// Test /backup/list
fetch('/admin/backup/list')
    .then(response => {
        console.log(`📡 /admin/backup/list - Status: ${response.status} ${response.statusText}`);
        return response.json();
    })
    .then(data => {
        console.log('✅ /admin/backup/list responde correctamente');
        console.log('   - Success:', data.success);
        console.log('   - Backups:', data.backups?.length || 0);
        console.log('   - Stats:', data.stats);
        
        if (data.backups && data.backups.length > 0) {
            console.log('   - Primer backup:', data.backups[0].filename);
        }
    })
    .catch(error => {
        console.error('❌ /admin/backup/list ERROR:', error);
    });

// Test /backup/system-status
fetch('/admin/backup/system-status')
    .then(response => {
        console.log(`📡 /admin/backup/system-status - Status: ${response.status} ${response.statusText}`);
        return response.json();
    })
    .then(data => {
        console.log('✅ /admin/backup/system-status responde correctamente');
        console.log('   - Success:', data.success);
        console.log('   - DB Status:', data.status?.database_status);
    })
    .catch(error => {
        console.error('❌ /admin/backup/system-status ERROR:', error);
    });

console.log('');

// 5. Test de CSRF Token
console.log('%c5️⃣ Verificando CSRF Token', 'color: #0d6efd; font-weight: bold;');
const csrfMeta = document.querySelector('meta[name="csrf-token"]');
if (csrfMeta) {
    const token = csrfMeta.getAttribute('content');
    console.log('✅ CSRF token presente');
    console.log('   - Token:', token.substring(0, 20) + '...' + token.substring(token.length - 10));
} else {
    console.error('❌ CSRF token NO ENCONTRADO');
}
console.log('');

// 6. Test manual de botones
console.log('%c6️⃣ Test de botones (manual)', 'color: #0d6efd; font-weight: bold;');
console.log('Ejecuta estos comandos para probar:');
console.log('');
console.log('%c  backupManager.showCreateBackupModal()', 'color: #28a745; background: #f0f0f0; padding: 2px 5px;');
console.log('  → Debe abrir modal de crear backup');
console.log('');
console.log('%c  backupManager.showUploadBackupModal()', 'color: #28a745; background: #f0f0f0; padding: 2px 5px;');
console.log('  → Debe abrir modal de subir backup');
console.log('');
console.log('%c  backupManager.loadBackups()', 'color: #28a745; background: #f0f0f0; padding: 2px 5px;');
console.log('  → Debe recargar lista de backups');
console.log('');

// 7. Verificar errores en consola
console.log('%c7️⃣ Errores en consola', 'color: #0d6efd; font-weight: bold;');
console.log('Revisa arriba si hay mensajes en ROJO ❌');
console.log('');

// 8. Resumen
setTimeout(() => {
    console.log('');
    console.log('%c📊 RESUMEN DEL DIAGNÓSTICO', 'background: #28a745; color: white; padding: 5px 10px; font-weight: bold;');
    console.log('');
    
    if (typeof backupManager !== 'undefined' && missingElements === 0 && typeof bootstrap !== 'undefined') {
        console.log('%c✅ TODO OK - El sistema debería funcionar', 'color: #28a745; font-weight: bold; font-size: 14px;');
        console.log('');
        console.log('Si los botones no funcionan, intenta:');
        console.log('1. Hacer click en "Crear Backup" o "Subir Backup"');
        console.log('2. Ejecutar: backupManager.showCreateBackupModal()');
        console.log('3. Revisar si hay errores en ROJO arriba');
    } else {
        console.log('%c⚠️ HAY PROBLEMAS', 'color: #dc3545; font-weight: bold; font-size: 14px;');
        console.log('');
        if (typeof backupManager === 'undefined') {
            console.log('❌ backupManager no existe');
        }
        if (missingElements > 0) {
            console.log(`❌ ${missingElements} elementos DOM faltantes`);
        }
        if (typeof bootstrap === 'undefined') {
            console.log('❌ Bootstrap no cargado');
        }
        console.log('');
        console.log('💡 Soluciones:');
        console.log('1. Recarga la página (Ctrl + Shift + R)');
        console.log('2. Verifica que el archivo backup-manager-v2.js se cargó');
        console.log('3. Revisa errores en rojo arriba ↑');
    }
}, 2000);
