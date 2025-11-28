/**
    // BackupManager v2.1.2 - Sistema de gestión de backups
 * Versión: 2.1.1
 * Fecha: 2025-11-07
 */

console.log('📦 [BackupManager JS] Módulo iniciándose... versión 2.1.1');
console.log('📦 [BackupManager JS] Verificando estado inicial:', {
    document: !!document,
    DOMContentLoaded: document.readyState,
    windowApi: !!window.api
});

class BackupManager {
    constructor() {
        console.log('🚀 [BackupManager] Iniciando constructor...');
        try {
            this.init();
            console.log('✅ [BackupManager] Constructor completado exitosamente');
        } catch (error) {
            console.error('❌ [BackupManager] Error en constructor:', error);
            throw error;
        }
    }
    
    init() {
        console.log('🔧 [BackupManager] Inicializando event listeners...');
        
        try {
            // Event listeners principales
            const backupForm = document.getElementById('backupForm');
            const btnGenerateBackup = document.getElementById('btnGenerateBackup');
            
            if (backupForm && btnGenerateBackup) {
                btnGenerateBackup.addEventListener('click', (e) => {
                    console.log('Generate backup button clicked');
                    e.preventDefault();
                    this.createBackupFromForm();
                });
                console.log('✅ Backup button event listener attached');
            } else {
                console.warn('⚠️ Backup form or button not found');
            }
            
            // Event listeners opcionales
            this.addOptionalEventListener('filterStatus', 'change', () => this.filterBackups());
            
        } catch (error) {
            console.error('❌ [BackupManager] Error en init():', error);
            throw error;
        }
    }
    
    addOptionalEventListener(elementId, event, handler) {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener(event, handler);
            console.log(`✅ Event listener agregado para ${elementId}`);
        } else {
            console.warn(`⚠️ Elemento ${elementId} no encontrado`);
        }
    }
    
    async loadBackups() {
        console.log('📡 [loadBackups] Cargando lista de backups...');
        const backupsContainer = document.getElementById('backupsList');
        
        if (backupsContainer) {
            backupsContainer.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Cargando backups...</span></div></div>';
        }

        try {
            // Debug: verificar que api esté disponible
            if (!window.api) {
                throw new Error('window.api no está disponible');
            }
            
            if (typeof window.api.get !== 'function') {
                throw new Error('window.api.get no es una función');
            }
            
            console.log('📡 [loadBackups] window.api disponible, enviando petición...');
            console.log('📡 [loadBackups] CSRF Token:', window.api.csrfToken);
            
            const result = await api.get('/admin/backup/list');
            
            console.log('📋 [loadBackups] Datos recibidos:', result);

            if (result.success && result.backups) {
                console.log(`✅ [loadBackups] ${result.backups.length} backups encontrados`);
                this.renderBackups(result.backups);
            } else {
                throw new Error(result.message || 'Error al cargar backups');
            }

        } catch (error) {
            console.error('❌ [loadBackups] Error completo:', error);
            console.error('❌ [loadBackups] Error stack:', error.stack);
            
            // Mostrar error más detallado
            let errorMessage = error.message;
            if (error.message.includes('401') || error.message.includes('login')) {
                errorMessage = 'Error de autenticación. Recarga la página e intenta de nuevo.';
            } else if (error.message.includes('403')) {
                errorMessage = 'No tienes permisos para ver los backups.';
            }
            
            if (backupsContainer) {
                backupsContainer.innerHTML = `
                    <div class="text-center py-5">
                        <i class="fas fa-exclamation-triangle fa-2x text-warning"></i>
                        <p class="text-muted mt-2">Error al cargar backups: ${errorMessage}</p>
                        <button class="btn btn-secondary btn-sm mt-2" onclick="window.backupManager.loadBackups()">🔄 Reintentar</button>
                        <div class="mt-2">
                            <small class="text-muted">Error técnico: ${error.message}</small>
                        </div>
                    </div>
                `;
            }
        }
    }    async loadStats() {
        try {
            console.log('📊 [loadStats] Cargando estadísticas...');
            const result = await api.get('/admin/backup/stats');
            
            if (result.success) {
                const stats = result.stats;
                document.getElementById('totalBackups').textContent = stats.total_backups;
                document.getElementById('lastBackupDate').textContent = stats.last_backup_date || 'Nunca';
                document.getElementById('totalSize').textContent = this.formatFileSize(stats.total_size);
                document.getElementById('dbStatus').textContent = stats.db_status;
                console.log('✅ [loadStats] Estadísticas actualizadas');
                
                // Forzar ocultamiento del loading overlay
                if (window.loading && typeof window.loading.hideAll === 'function') {
                    window.loading.hideAll();
                }
            }
        } catch (error) {
            console.error('❌ [loadStats] Error:', error);
        }
    }
    
    renderBackups(backups) {
        console.log('🎨 [renderBackups] Iniciando con datos:', backups);
        const container = document.getElementById('backupsList');
        console.log('🎨 [renderBackups] Container encontrado:', !!container);
        
        if (!container) {
            console.error('❌ [renderBackups] Container backupsList NO EXISTE en el DOM');
            return;
        }
        
        if (!backups || backups.length === 0) {
            console.log('📝 [renderBackups] No hay backups para mostrar');
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-database fa-2x text-muted"></i>
                    <p class="text-muted mt-2">No hay backups disponibles</p>
                </div>
            `;
            return;
        }
        
        console.log(`📋 [renderBackups] Generando HTML para ${backups.length} backups`);
        
        try {
            const html = backups.map((backup, index) => {
                console.log(`  📄 [renderBackups] Procesando backup ${index + 1}:`, backup.name);
                return `
            <div class="backup-card p-3 border-bottom" data-status="${backup.status}">
                <div class="row align-items-center">
                    <div class="col-md-4">
                        <div class="d-flex align-items-center">
                            <i class="fas fa-file-archive fa-lg text-primary me-3"></i>
                            <div>
                                <h6 class="mb-1">${backup.name}</h6>
                                <small class="text-muted">${backup.created_at}</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="backup-size">${this.formatFileSize(backup.size)}</div>
                        <div class="backup-status status-${backup.status} mt-1">
                            ${backup.status}
                        </div>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted">${backup.description || 'Sin descripción'}</small>
                    </div>
                    <div class="col-md-2 text-end">
                        <div class="backup-actions">
                            <button class="btn btn-sm btn-outline-primary" 
                                    onclick="window.backupManager.downloadBackup('${backup.filename}')"
                                    title="Descargar">
                                <i class="fas fa-download"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-success" 
                                    onclick="window.backupManager.quickRestore('${backup.filename}')"
                                    title="Restaurar">
                                <i class="fas fa-undo"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" 
                                    onclick="window.backupManager.deleteBackup('${backup.filename}')"
                                    title="Eliminar">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
            }).join('');
            
            console.log(`✅ [renderBackups] HTML generado, longitud: ${html.length} caracteres`);
            console.log(`🔧 [renderBackups] Insertando HTML en container...`);
            
            container.innerHTML = html;
            
            console.log(`✅ [renderBackups] HTML insertado exitosamente`);
            console.log(`📊 [renderBackups] ${backups.length} backups renderizados en el DOM`);
            console.log(`🔍 [renderBackups] Verificación: container.children.length =`, container.children.length);
            console.log(`🔍 [renderBackups] Primera tarjeta:`, container.children[0]?.className);
            
            // Forzar ocultamiento del loading overlay global
            if (window.loading && typeof window.loading.hideAll === 'function') {
                window.loading.hideAll();
                console.log('✅ [renderBackups] Loading overlay ocultado');
            }
            
        } catch (error) {
            console.error('❌ [renderBackups] Error al generar/insertar HTML:', error);
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-exclamation-triangle fa-2x text-danger"></i>
                    <p class="text-danger mt-2">Error al renderizar backups: ${error.message}</p>
                </div>
            `;
        }
    }
    
    filterBackups() {
        const filter = document.getElementById('filterStatus').value;
        const cards = document.querySelectorAll('.backup-card');
        
        cards.forEach(card => {
            if (!filter || card.dataset.status === filter) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    async downloadBackup(filename) {
        try {
            const link = document.createElement('a');
            link.href = `/admin/backup/download/${filename}`;
            link.download = filename;
            link.click();
            toast.success('Descarga iniciada');
        } catch (error) {
            console.error('Error:', error);
            toast.error('Error al descargar backup');
        }
    }
    
    async deleteBackup(filename) {
        const confirmed = await confirm.delete(`¿Eliminar el backup "${filename}"?`);
        if (!confirmed) return;
        
        try {
            const result = await api.delete(`/admin/backup/delete/${filename}`);
            if (result.success) {
                toast.success(result.message);
                this.loadBackups();
            } else {
                toast.error(result.message);
            }
        } catch (error) {
            console.error('Error:', error);
            toast.error('Error al eliminar backup');
        }
    }
    
    async quickRestore(filename) {
        console.log('🔄 [quickRestore] Iniciando restauración de:', filename);
        
        // Confirmación con advertencia severa
        const confirmed = await window.confirm.confirm(
            `⚠️ <strong>ADVERTENCIA CRÍTICA</strong><br><br>
            ¿Está seguro de restaurar el backup <strong>"${filename}"</strong>?<br><br>
            <span class="text-danger">Esta acción:</span>
            <ul class="text-start">
                <li>Sobrescribirá TODA la base de datos actual</li>
                <li>Se perderán los cambios no guardados</li>
                <li>Puede tomar varios minutos</li>
                <li>NO se puede deshacer</li>
            </ul>`,
            'Confirmar Restauración de Backup',
            {
                icon: 'fa-database',
                headerClass: 'bg-danger text-white',
                confirmClass: 'btn-danger',
                confirmText: 'Restaurar Backup'
            }
        );
        
        if (!confirmed) {
            console.log('❌ [quickRestore] Restauración cancelada por el usuario');
            return;
        }
        
        try {
            console.log('📡 [quickRestore] Enviando petición de restauración...');
            
            // Mostrar loading
            if (window.loading) {
                window.loading.show('restore');
            }
            
            // Mostrar toast informativo
            toast.info('⏳ Restaurando backup... Esto puede tomar varios minutos. No cierre la página.');
            
            // Enviar petición de restauración con timeout extendido
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 360000); // 6 minutos (mayor que servidor)
            
            const response = await fetch('/admin/backup/restore-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.api.csrfToken
                },
                body: JSON.stringify({ filename: filename }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            console.log('📋 [quickRestore] Respuesta recibida:', result);
            
            // Ocultar loading
            if (window.loading) {
                window.loading.hide('restore');
            }
            
            if (result.success) {
                toast.success(`✅ Backup restaurado exitosamente: ${filename}`);
                
                // Mostrar advertencia de recarga
                setTimeout(() => {
                    window.confirm.confirm(
                        '✅ Base de datos restaurada correctamente.<br><br>Se recomienda recargar la página para ver los cambios.',
                        'Restauración Completada',
                        {
                            icon: 'fa-check-circle',
                            headerClass: 'bg-success text-white',
                            confirmClass: 'btn-success',
                            confirmText: 'Recargar Página',
                            cancelText: 'Más Tarde'
                        }
                    ).then(reload => {
                        if (reload) {
                            window.location.reload();
                        }
                    });
                }, 500);
                
                // Recargar lista de backups
                this.loadBackups();
                
            } else {
                toast.error(`❌ Error: ${result.message || 'No se pudo restaurar el backup'}`);
            }
            
        } catch (error) {
            console.error('❌ [quickRestore] Error:', error);
            
            // Ocultar loading en caso de error
            if (window.loading) {
                window.loading.hide('restore');
            }
            
            // Mensajes de error específicos
            let errorMessage = 'Error desconocido';
            
            if (error.name === 'AbortError') {
                errorMessage = 'La operación tomó demasiado tiempo (timeout de 4 minutos). El backup podría ser muy grande o el servidor estar ocupado.';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Error de conexión con el servidor. Verifique su conexión a internet o que el servidor esté funcionando.';
            } else if (error.message.includes('NetworkError')) {
                errorMessage = 'Error de red. El servidor podría no estar respondiendo.';
            } else {
                errorMessage = error.message || 'Error al restaurar el backup';
            }
            
            toast.error(`❌ ${errorMessage}`);
        }
    }
    
    async createBackupFromForm() {
        console.log('📦 [createBackupFromForm] Iniciando creación de backup...');
        
        try {
            // Obtener datos del formulario
            const form = document.getElementById('backupForm');
            if (!form) {
                console.error('❌ [createBackupFromForm] Formulario de backup no encontrado');
                toast.error('Error: Formulario de backup no encontrado');
                return;
            }
            
            const formData = new FormData(form);
            const backupData = {
                name: formData.get('name') || '',
                description: formData.get('description') || '',
                tipo: formData.get('tipo') || 'manual'
            };
            
            console.log('📋 [createBackupFromForm] Datos del formulario:', backupData);
            
            // Validaciones básicas
            if (backupData.name.length > 100) {
                toast.error('El nombre no puede exceder 100 caracteres');
                return;
            }
            
            if (backupData.description.length > 255) {
                toast.error('La descripción no puede exceder 255 caracteres');
                return;
            }
            
            // Mostrar loading
            if (window.loading) {
                window.loading.show('create');
            }
            
            // Mostrar toast informativo
            toast.info('⏳ Creando backup... Esto puede tomar varios minutos. No cierre la página.');
            
            // Deshabilitar botón durante la creación
            let createBtn = document.getElementById('btnGenerateBackup');
            if (createBtn) {
                createBtn.disabled = true;
                createBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creando...';
            }
            
            console.log('📡 [createBackupFromForm] Enviando petición de creación...');
            
            // Crear FormData para envío compatible con backend Flask
            const formDataToSend = new FormData();
            formDataToSend.append('name', backupData.name || '');
            formDataToSend.append('description', backupData.description || '');
            formDataToSend.append('tipo', backupData.tipo || 'manual');
            formDataToSend.append('include_data', 'on'); // Siempre incluir datos
            formDataToSend.append('compress', 'on'); // Siempre comprimir
            
            console.log('📡 [createBackupFromForm] FormData creado:', {
                name: formDataToSend.get('name'),
                description: formDataToSend.get('description'),
                tipo: formDataToSend.get('tipo')
            });
            
            // Enviar petición de creación con timeout extendido
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutos
            
            const response = await fetch('/admin/backup/create', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.api.csrfToken
                    // NO incluir Content-Type para que el navegador establezca multipart/form-data automáticamente
                },
                body: formDataToSend,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('📋 [createBackupFromForm] Respuesta recibida:', result);

            if (result.success) {
                // Mostrar mensaje de éxito
                if (window.toast) {
                    toast.success(`✅ Backup creado exitosamente: ${result.filename || 'archivo generado'}`);
                } else {
                    console.log('✅ Backup creado exitosamente:', result.filename || 'archivo generado');
                    alert('✅ Backup creado exitosamente: ' + (result.filename || 'archivo generado'));
                }
                
                // Limpiar formulario
                form.reset();
                
                // No hay modal que cerrar en esta implementación (formulario en línea)
                console.log('📋 [createBackupFromForm] Formulario limpiado');
                
                // Mostrar feedback visual inmediato
                const createSection = document.getElementById('createBackupSection');
                if (createSection) {
                    createSection.style.opacity = '0.7';
                    setTimeout(() => {
                        createSection.style.opacity = '1';
                    }, 300);
                }
                
                // Recargar datos de forma síncrona para asegurar que se complete
                console.log('📋 [createBackupFromForm] Recargando lista de backups...');
                await Promise.all([
                    this.loadBackups().catch(err => console.error('Error recargando backups:', err)),
                    this.loadStats().catch(err => console.error('Error recargando stats:', err))
                ]);
                console.log('📋 [createBackupFromForm] Recarga completada');
                
                // Scroll suave hacia la lista de backups para mostrar el nuevo backup
                const backupsList = document.getElementById('backupsList');
                if (backupsList) {
                    backupsList.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
                
            } else {
                if (window.toast) {
                    toast.error(`❌ Error: ${result.message || 'No se pudo crear el backup'}`);
                } else {
                    alert(`❌ Error: ${result.message || 'No se pudo crear el backup'}`);
                }
            }
            
        } catch (error) {
            console.error('❌ [createBackupFromForm] Error:', error);
            
            // Mensajes de error específicos
            let errorMessage = 'Error desconocido';
            
            if (error.name === 'AbortError') {
                errorMessage = 'La operación tomó demasiado tiempo (timeout de 5 minutos). La base de datos podría ser muy grande.';
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Error de conexión con el servidor. Verifique su conexión a internet.';
            } else if (error.message.includes('NetworkError')) {
                errorMessage = 'Error de red. El servidor podría no estar respondiendo.';
            } else {
                errorMessage = error.message || 'Error al crear el backup';
            }
            
            toast.error(`❌ ${errorMessage}`);
            
        } finally {
            // Limpieza final garantizada con debugging extensivo
            console.log('📋 [createBackupFromForm] Ejecutando limpieza final...');
            
            // Forzar ocultamiento de todos los loading posibles
            if (window.loading) {
                console.log('📋 [createBackupFromForm] Ocultando window.loading...');
                window.loading.hide('create');
                window.loading.hide(); // Sin parámetro por si acaso
            }
            
            // Buscar y ocultar cualquier overlay de loading
            const loadingOverlays = document.querySelectorAll('[id*="loading"], .loading, .spinner, [class*="loading"]');
            loadingOverlays.forEach((overlay, index) => {
                console.log(`📋 [createBackupFromForm] Ocultando overlay ${index}:`, overlay.className || overlay.id);
                overlay.style.display = 'none';
                overlay.style.visibility = 'hidden';
                overlay.classList.add('d-none');
            });
            
            // Restaurar botón con debugging
            const finalBtn = document.getElementById('btnGenerateBackup');
            if (finalBtn) {
                console.log('📋 [createBackupFromForm] Estado botón antes:', {
                    disabled: finalBtn.disabled,
                    innerHTML: finalBtn.innerHTML,
                    className: finalBtn.className
                });
                
                finalBtn.disabled = false;
                finalBtn.innerHTML = '<i class="fas fa-plus"></i> Crear Backup';
                finalBtn.classList.remove('loading', 'disabled');
                
                console.log('📋 [createBackupFromForm] Estado botón después:', {
                    disabled: finalBtn.disabled,
                    innerHTML: finalBtn.innerHTML
                });
            }
            
            // Forzar un repaint del DOM
            document.body.style.display = 'none';
            document.body.offsetHeight; // Trigger reflow
            document.body.style.display = '';
            
            console.log('✅ [createBackupFromForm] Limpieza completada con repaint forzado');
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
}

// Inicialización automática cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 [Init] DOM cargado, inicializando BackupManager desde JS externo...');
    console.log('🔍 [Init] Verificando elementos del DOM:');
    console.log('  - backupsList:', !!document.getElementById('backupsList'));
    console.log('  - btnGenerateBackup:', !!document.getElementById('btnGenerateBackup'));
    console.log('  - window.api:', !!window.api);
    
    // Esperar a que window.api esté disponible
    const initBackupManager = () => {
        console.log('🔄 [Init] Verificando disponibilidad de window.api...');
        
        if (!window.api) {
            console.warn('⚠️ [Init] window.api no disponible aún, esperando...');
            setTimeout(initBackupManager, 100);
            return;
        }
        
        console.log('✅ [Init] window.api encontrado:', Object.keys(window.api));
        
        if (typeof window.api.get !== 'function') {
            console.warn('⚠️ [Init] window.api.get no es función, esperando...');
            setTimeout(initBackupManager, 100);
            return;
        }
        
        console.log('✅ [Init] window.api.get es función, procediendo...');
        
        try {
            window.backupManager = new BackupManager();
            console.log('✅ [Init] BackupManager creado y disponible globalmente');
            
            // Cargar datos automáticamente
            console.log('🚀 [Init] Iniciando carga de datos...');
            window.backupManager.loadBackups();
            window.backupManager.loadStats();
            
        } catch (error) {
            console.error('❌ [Init] Error creando BackupManager:', error);
            console.error('❌ [Init] Stack:', error.stack);
        }
    };
    
    // Iniciar la verificación
    initBackupManager();
});

console.log('✅ [BackupManager JS] Módulo cargado completamente');
