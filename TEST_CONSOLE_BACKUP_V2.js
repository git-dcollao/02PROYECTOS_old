/**
 * TEST MANUAL - Backup Manager V2
 * ================================
 * Ejecutar estos comandos en la consola del navegador (F12)
 * cuando estés en: http://localhost:5050/admin/backup/v2
 */

// ========================================
// TEST 1: Verificar que el Manager existe
// ========================================
console.log('🧪 TEST 1: Verificar BackupManagerV2');
console.log('backupManager existe:', typeof backupManager !== 'undefined');
console.log('backupManager.backups:', backupManager?.backups?.length || 0);
console.log('backupManager.currentPage:', backupManager?.currentPage || 'N/A');

// ========================================
// TEST 2: Verificar carga de datos
// ========================================
console.log('\n🧪 TEST 2: Cargar backups manualmente');
if (backupManager) {
    backupManager.loadBackups().then(() => {
        console.log('✅ Backups cargados:', backupManager.backups.length);
        console.log('Primer backup:', backupManager.backups[0]);
    });
}

// ========================================
// TEST 3: Verificar stats
// ========================================
console.log('\n🧪 TEST 3: Verificar estadísticas');
setTimeout(() => {
    console.log('Total Backups:', document.getElementById('totalBackups')?.textContent);
    console.log('Último Backup:', document.getElementById('lastBackupDate')?.textContent);
    console.log('Tamaño Total:', document.getElementById('totalSize')?.textContent);
    console.log('Estado BD:', document.getElementById('dbStatus')?.textContent);
}, 2000);

// ========================================
// TEST 4: Verificar tabla
// ========================================
console.log('\n🧪 TEST 4: Verificar tabla de backups');
setTimeout(() => {
    const rows = document.querySelectorAll('#backupsList tr');
    console.log('Filas en tabla:', rows.length);
    console.log('Primera fila:', rows[0]?.outerHTML.substring(0, 100) + '...');
}, 2000);

// ========================================
// TEST 5: Verificar modales
// ========================================
console.log('\n🧪 TEST 5: Verificar modales');
const modals = [
    'modalCreateBackup',
    'modalUploadBackup',
    'modalRestoreProgress',
    'modalDeleteConfirm',
    'modalRestoreConfirm'
];
modals.forEach(modalId => {
    const modal = document.getElementById(modalId);
    console.log(`Modal ${modalId}:`, modal ? '✅ Existe' : '❌ No existe');
});

// ========================================
// TEST 6: Verificar botones principales
// ========================================
console.log('\n🧪 TEST 6: Verificar botones');
const buttons = [
    'btnCreateBackup',
    'btnUploadBackup',
    'btnRefresh'
];
buttons.forEach(btnId => {
    const btn = document.getElementById(btnId);
    console.log(`Botón ${btnId}:`, btn ? '✅ Existe' : '❌ No existe');
});

// ========================================
// TEST 7: Verificar paginación
// ========================================
console.log('\n🧪 TEST 7: Verificar paginación');
setTimeout(() => {
    const pagination = document.getElementById('paginationControls');
    const paginationInfo = document.getElementById('paginationInfo');
    console.log('Paginación HTML:', pagination ? '✅ Existe' : '❌ No existe');
    console.log('Info paginación:', paginationInfo?.textContent);
}, 2000);

// ========================================
// TEST 8: Simular creación de backup
// ========================================
console.log('\n🧪 TEST 8: Simular modal de creación');
setTimeout(() => {
    if (backupManager) {
        console.log('Abriendo modal de crear backup...');
        backupManager.showCreateBackupModal();
        setTimeout(() => {
            const modal = document.getElementById('modalCreateBackup');
            console.log('Modal visible:', modal?.classList.contains('show'));
        }, 500);
    }
}, 3000);

// ========================================
// TEST 9: Verificar CSRF token
// ========================================
console.log('\n🧪 TEST 9: Verificar CSRF token');
const csrfMeta = document.querySelector('meta[name="csrf-token"]');
console.log('CSRF token:', csrfMeta ? '✅ Presente' : '❌ No presente');
console.log('CSRF value:', csrfMeta?.getAttribute('content')?.substring(0, 20) + '...');

// ========================================
// TEST 10: Verificar API calls
// ========================================
console.log('\n🧪 TEST 10: Test llamadas API');
fetch('/admin/backup/list')
    .then(r => r.json())
    .then(data => {
        console.log('API /backup/list responde:', data.success ? '✅ OK' : '❌ ERROR');
        console.log('Backups en respuesta:', data.backups?.length || 0);
        console.log('Stats en respuesta:', data.stats);
    })
    .catch(err => console.error('❌ Error en API:', err));

fetch('/admin/backup/system-status')
    .then(r => r.json())
    .then(data => {
        console.log('API /system-status responde:', data.success ? '✅ OK' : '❌ ERROR');
        console.log('Estado DB:', data.status?.database_status);
    })
    .catch(err => console.error('❌ Error en API:', err));

// ========================================
// RESUMEN
// ========================================
console.log('\n' + '='.repeat(50));
console.log('📊 RESUMEN DE TESTS');
console.log('='.repeat(50));
console.log('Todos los tests se ejecutarán en 3 segundos.');
console.log('Revisa los resultados arriba ☝️');
console.log('='.repeat(50));
