/**
 * Backup Manager Mejorado - Senior Implementation FIXED
 * =====================================================
 * 
 * Características:
 * ✅ Progress tracking en tiempo real
 * ✅ Sistema de logging detallado
 * ✅ Monitoring de recursos del sistema
 * ✅ UI responsiva con feedback inmediato
 * ✅ Error handling robusto
 * ✅ Optimizaciones de performance
 * ✅ Autenticación AJAX con CSRF tokens
 */

// 🔐 Función para obtener token CSRF
function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    if (csrfToken) {
        return csrfToken.getAttribute('content');
    }
    
    // Fallback: buscar en inputs hidden
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    console.warn('⚠️ [CSRF] Token CSRF no encontrado');
    return null;
}

// 🔐 Configurar headers por defecto para AJAX
function getAuthHeaders() {
    const csrfToken = getCSRFToken();
    const headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    };
    
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
        console.log('🔐 [Auth] Token CSRF agregado a headers');
    }
    
    return headers;
}

class EnhancedBackupManager {
    constructor() {
        console.log('🚀 [EnhancedBackupManager] Inicializando manager mejorado...');
        
        this.progressModal = null;
        this.progressInterval = null;
        this.isOperationActive = false;
        this.currentOperation = null;
        this.lastProgressPercent = 0;
        this.loadingBackups = false; // ⚠️ PROTECCIÓN: Flag para evitar cargas múltiples
        
        // Configuración de polling
        this.progressPollingConfig = {
            interval: 2000,     // 2 segundos
            timeout: 600000     // 10 minutos
        };
        
        // Elementos DOM
        this.elements = {};
        
        this.init();
    }
    
    init() {
        /**
         * Inicializar el manager
         */
        console.log('🔧 [EnhancedBackupManager] Configurando elementos del DOM...');
        
        // Cachear elementos del DOM
        this.elements = {
            backupsList: document.getElementById('backupsList')
        };
        
        // Crear modal de progreso
        this.createProgressModal();
        
        // Cargar datos iniciales
        this.loadBackups();
        this.loadSystemStatus();
        
        // Configurar eventos
        this.bindEvents();
        
        console.log('✅ [EnhancedBackupManager] Inicialización completada');
    }
    
    async restoreBackup(filename, cleanDatabase = false) {
        /**
         * Restaurar backup con tracking de progreso en tiempo real
         * ⚠️ PROTECCIÓN: Solo procesar el archivo específico seleccionado
         * @param {string} filename - Archivo a restaurar
         * @param {boolean} cleanDatabase - Si true, limpia toda la BD antes de restaurar
         */
        console.log(`🔄 [EnhancedBackupManager] Iniciando restauración: ${filename}`);
        console.log(`🔍 [DEBUG] Limpieza de BD: ${cleanDatabase ? 'SÍ' : 'NO'}`);
        console.log(`🔍 [DEBUG] Instancia actual:`, this);
        console.log(`🔍 [DEBUG] Operación activa:`, this.isOperationActive);
        
        try {
            // ⚠️ PROTECCIÓN CRÍTICA: Verificar que no hay otra operación
            if (this.isOperationActive) {
                console.warn('⚠️ [PROTECCIÓN] Ya hay una operación de restauración en curso');
                this.showAlert('Ya hay una operación en curso. Espere a que termine.', 'warning');
                return;
            }
            
            // ⚠️ PROTECCIÓN: Validar filename específico
            if (!filename || typeof filename !== 'string' || filename.trim() === '') {
                console.error('❌ [PROTECCIÓN] Filename inválido:', filename);
                this.showAlert('Error: Archivo no especificado correctamente', 'error');
                return;
            }
            
            console.log(`✅ [PROTECCIÓN] Procesando SOLO el archivo: "${filename}"`);
            
            // Verificar estado inicial de la BD
            console.log('🔍 [Debug] Verificando estado inicial de la BD...');
            await this.debugDatabaseStatus('ANTES de la restauración');
            
            // Validaciones iniciales
            if (this.isOperationActive) {
                this.showAlert('Ya hay una operación en curso', 'warning');
                return;
            }
            
            // Confirmar operación
            var confirmed = await this.showConfirmDialog(
                'Confirmación de Restauración',
                '¿Está seguro de restaurar el backup "' + filename + '"?\n\n⚠️ ADVERTENCIA: Esta operación sobrescribirá todos los datos actuales de la base de datos.'
            );
            
            if (!confirmed) {
                console.log('ℹ️ [EnhancedBackupManager] Restauración cancelada por el usuario');
                return;
            }
            
            // Inicializar tracking de progreso
            this.isOperationActive = true;
            this.currentOperation = 'Restauración de ' + filename;
            
            // Mostrar modal de progreso
            this.showProgressModal();
            this.startProgressTracking();
            
            // Agregar log inicial
            this.addToActivityLog('Iniciando restauración de backup...');
            this.addToActivityLog('Archivo: ' + filename);
            
            // Realizar petición de restauración
            console.log('📡 [EnhancedBackupManager] Enviando petición de restauración...');
            
            // 🔐 Configurar headers de autenticación para restauración
            const authHeaders = getAuthHeaders();
            authHeaders['Content-Type'] = 'application/json';
            
            var response = await fetch('/admin/backup/restore-file', {
                method: 'POST',
                headers: authHeaders,
                credentials: 'same-origin',
                body: JSON.stringify({ 
                    filename: filename,
                    clean_database: cleanDatabase 
                })
            });
            
            var result = await response.json();
            
            // Detener tracking
            this.stopProgressTracking();
            
            if (response.ok && result.success) {
                console.log('✅ [EnhancedBackupManager] Restauración exitosa:', result);
                
                this.addToActivityLog('✅ Restauración completada exitosamente');
                this.addToActivityLog('🔄 Cerrando sesión para actualizar permisos...');
                
                // Mostrar estadísticas si están disponibles
                if (result.stats) {
                    this.addToActivityLog('📊 Estadísticas:');
                    this.addToActivityLog('   • Tiempo total: ' + result.stats.total_time);
                    this.addToActivityLog('   • Statements ejecutados: ' + result.stats.statements_executed);
                    this.addToActivityLog('   • Throughput: ' + result.stats.throughput);
                }
                
                // Actualizar progreso a 100% manualmente
                var progressBar = document.getElementById('progressBar');
                var progressPercent = document.getElementById('progressPercent');
                var currentOperation = document.getElementById('currentOperation');
                
                if (progressBar && progressPercent) {
                    progressBar.style.width = '100%';
                    progressPercent.textContent = '100%';
                    console.log('✅ [Manual] Progreso fijado a 100%');
                }
                if (currentOperation) {
                    currentOperation.textContent = 'Restauración completada - Cerrando sesión...';
                    console.log('✅ [Manual] Operación actualizada: Completada');
                }
                
                var self = this;
                // Redirigir al login después de 3 segundos
                setTimeout(function() {
                    self.hideProgressModal();
                    self.showAlert('Backup restaurado exitosamente - Volviendo al login...', 'success');
                    
                    // Redirigir al login para forzar nueva sesión con permisos actualizados
                    setTimeout(function() {
                        window.location.href = '/auth/logout?next=/auth/login';
                    }, 1500);
                }, 3000);
                
            } else {
                console.error('❌ [EnhancedBackupManager] Error en restauración:', result);
                
                // Manejo de errores específicos
                let errorMessage = result.message || 'Error desconocido';
                let logMessage = '❌ Error: ' + errorMessage;
                let suggestion = '';
                
                if (errorMessage.toLowerCase().includes('timeout') || 
                    errorMessage.toLowerCase().includes('timed out') ||
                    errorMessage.toLowerCase().includes('lost connection') ||
                    errorMessage.toLowerCase().includes('lock wait timeout') ||
                    errorMessage.toLowerCase().includes('deadlock')) {
                    logMessage = '❌ Error de timeout/bloqueo durante operación';
                    suggestion = 'La operación tomó demasiado tiempo. Reinicie la aplicación y use restauración aditiva.';
                } else if (errorMessage.toLowerCase().includes('duplicate') || 
                          errorMessage.toLowerCase().includes('duplicado')) {
                    suggestion = 'Considere usar restauración completa para evitar duplicados.';
                } else if (errorMessage.toLowerCase().includes('trabajador') ||
                          errorMessage.toLowerCase().includes('authentication')) {
                    suggestion = 'Error relacionado con usuarios del sistema. Use restauración aditiva.';
                }
                
                this.addToActivityLog(logMessage);
                
                var self = this;
                setTimeout(function() {
                    self.hideProgressModal();
                    self.showAlert(errorMessage, 'danger');
                    
                    if (suggestion) {
                        setTimeout(() => {
                            self.showAlert(suggestion, 'warning');
                        }, 2500);
                    }
                }, 2000);
            }
            
        } catch (error) {
            console.error('💥 [EnhancedBackupManager] Error en restauración:', error);
            
            // Manejo específico de errores de conexión/timeout
            let logMessage = '💥 Error de conexión durante la restauración';
            let alertMessage = 'Error de conexión durante la restauración';
            
            if (error.toString().toLowerCase().includes('timeout') ||
                error.toString().toLowerCase().includes('network')) {
                logMessage = '💥 Error de timeout/red durante la restauración';
                alertMessage = 'Timeout durante la restauración. Intente con modo aditivo.';
            }
            
            this.addToActivityLog(logMessage);
            this.stopProgressTracking();
            
            var self = this;
            setTimeout(function() {
                self.hideProgressModal();
                self.showAlert(alertMessage, 'danger');
            }, 1000);
        } finally {
            this.isOperationActive = false;
        }
    }
    
    startProgressTracking() {
        /**
         * Iniciar polling de progreso en tiempo real
         */
        console.log('📡 [EnhancedBackupManager] Iniciando tracking de progreso...');
        console.log('🔍 [startProgressTracking] Configuración polling:', this.progressPollingConfig);
        
        // Detener polling anterior si existe
        if (this.progressInterval) {
            console.log('🛑 [startProgressTracking] Deteniendo polling anterior...');
            clearInterval(this.progressInterval);
        }
        
        var self = this;
        // Primera actualización inmediata
        console.log('⚡ [startProgressTracking] Primera actualización inmediata...');
        this.updateProgress().catch(function(error) {
            console.error('❌ [startProgressTracking] Error en primera actualización:', error);
        });
        
        // Actualizar cada 2 segundos
        console.log('⏰ [startProgressTracking] Configurando polling cada', this.progressPollingConfig.interval, 'ms');
        this.progressInterval = setInterval(function() {
            console.log('🔄 [Polling] Ejecutando actualización programada...');
            self.updateProgress().catch(function(error) {
                console.error('❌ [EnhancedBackupManager] Error actualizando progreso:', error);
            });
        }, this.progressPollingConfig.interval);
        
        console.log('✅ [startProgressTracking] Polling iniciado. ID:', this.progressInterval);
        
        // Timeout de seguridad (10 minutos)
        setTimeout(function() {
            if (self.progressInterval) {
                console.warn('⏰ [EnhancedBackupManager] Timeout de progreso alcanzado');
                self.stopProgressTracking();
            }
        }, this.progressPollingConfig.timeout);
    }
    
    async updateProgress() {
        /**
         * Actualizar información de progreso desde el servidor
         */
        try {
            console.log('🔄 [updateProgress] Consultando progreso...');
            console.log('🔍 [updateProgress] URL corregida: /admin/backup/progress');
            
            // 🔐 Configurar headers de autenticación
            const headers = getAuthHeaders();
            console.log('🔐 [updateProgress] Headers configurados:', headers);
            
            var response = await fetch('/admin/backup/progress', {
                method: 'GET',
                headers: headers,
                credentials: 'same-origin'  // Incluir cookies de sesión
            });
            console.log('📡 [updateProgress] Respuesta HTTP:', response.status, response.statusText);
            
            if (response.ok) {
                var data = await response.json();
                console.log('📊 [updateProgress] Datos recibidos:', JSON.stringify(data, null, 2));
                
                if (data.success && data.progress) {
                    var progress = data.progress;
                    
                    console.log('📊 [updateProgress] Progreso: ' + progress.progress_percent + '% - ' + progress.current_operation);
                    console.log('🔍 [updateProgress] Operación activa:', progress.is_active);
                    
                    // Actualizar barra de progreso
                    var progressBar = document.getElementById('progressBar');
                    var progressPercent = document.getElementById('progressPercent');
                    
                    console.log('🔍 [updateProgress] Elementos DOM:', {
                        progressBar: !!progressBar,
                        progressPercent: !!progressPercent
                    });
                    
                    if (progressBar && progressPercent) {
                        progressBar.style.width = progress.progress_percent + '%';
                        progressPercent.textContent = Math.round(progress.progress_percent) + '%';
                        console.log('✅ [updateProgress] Barra actualizada: ' + progress.progress_percent + '%');
                    } else {
                        console.warn('⚠️ [updateProgress] Elementos de progreso no encontrados');
                        console.log('🔍 [updateProgress] progressBar element:', progressBar);
                        console.log('🔍 [updateProgress] progressPercent element:', progressPercent);
                    }
                    
                    // Actualizar operación actual
                    var currentOperation = document.getElementById('currentOperation');
                    if (currentOperation) {
                        currentOperation.textContent = progress.current_operation;
                        console.log('📝 [updateProgress] Operación actualizada: ' + progress.current_operation);
                    }
                    
                    // Agregar al log de actividad si hay cambios significativos
                    if (progress.progress_percent > (this.lastProgressPercent || 0) + 5) {
                        this.addToActivityLog('📊 Progreso: ' + Math.round(progress.progress_percent) + '%');
                        this.lastProgressPercent = progress.progress_percent;
                    }
                    
                    // Detectar finalización
                    if (progress.progress_percent >= 100 || !progress.is_active) {
                        console.log('✅ [updateProgress] Operación completada, deteniendo polling');
                        this.addToActivityLog('🎉 Operación completada!');
                        this.stopProgressTracking();
                        
                        // Auto-cerrar modal después de 2 segundos
                        var self = this;
                        setTimeout(function() {
                            self.hideProgressModal();
                            self.showAlert('Operación completada exitosamente', 'success');
                            self.loadBackups(); // Recargar lista
                        }, 2000);
                    }
                    
                } else {
                    console.warn('⚠️ [updateProgress] Respuesta sin datos de progreso válidos:', data);
                    // Si no hay progreso válido, verificar si la operación ya terminó
                    if (!this.isOperationActive) {
                        console.log('🏁 [updateProgress] Operación ya no activa, cerrando...');
                        this.stopProgressTracking();
                        var self = this;
                        setTimeout(function() {
                            self.hideProgressModal();
                        }, 1000);
                    }
                }
                
            } else {
                console.error('❌ [updateProgress] Error HTTP:', response.status, response.statusText);
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            
        } catch (error) {
            console.error('❌ [updateProgress] Error:', error);
            this.stopProgressTracking();
        }
    }
    
    stopProgressTracking() {
        /**
         * Detener polling de progreso
         */
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
            console.log('🛑 [EnhancedBackupManager] Progress tracking detenido');
        }
    }
    
    showProgressModal() {
        /**
         * Mostrar modal de progreso
         */
        console.log('🎭 [EnhancedBackupManager] Mostrando modal de progreso...');
        
        // Reset modal antes de mostrar
        this.resetProgressModal();
        
        if (this.progressModal) {
            console.log('✅ [showProgressModal] Modal encontrado, mostrando...');
            var modal = new bootstrap.Modal(this.progressModal);
            modal.show();
            
            // Verificar elementos DOM después de mostrar
            setTimeout(function() {
                var progressBar = document.getElementById('progressBar');
                var progressPercent = document.getElementById('progressPercent');
                var currentOperation = document.getElementById('currentOperation');
                
                console.log('🔍 [showProgressModal] Verificación DOM post-show:', {
                    progressBar: !!progressBar,
                    progressPercent: !!progressPercent,
                    currentOperation: !!currentOperation
                });
            }, 100);
            
            console.log('✅ [EnhancedBackupManager] Modal de progreso mostrado');
        } else {
            console.error('❌ [EnhancedBackupManager] Modal de progreso no encontrado');
        }
    }
    
    hideProgressModal() {
        /**
         * Ocultar modal de progreso
         */
        if (this.progressModal) {
            var modal = bootstrap.Modal.getInstance(this.progressModal);
            if (modal) {
                modal.hide();
            }
            console.log('🙈 [EnhancedBackupManager] Modal de progreso ocultado');
        }
    }
    
    resetProgressModal() {
        /**
         * Reset modal de progreso
         */
        var progressBar = document.getElementById('progressBar');
        var progressPercent = document.getElementById('progressPercent');
        var currentOperation = document.getElementById('currentOperation');
        var activityLog = document.getElementById('activityLog');
        
        if (progressBar) progressBar.style.width = '0%';
        if (progressPercent) progressPercent.textContent = '0%';
        if (currentOperation) currentOperation.textContent = 'Iniciando...';
        if (activityLog) activityLog.innerHTML = '';
        
        this.lastProgressPercent = 0;
    }
    
    createProgressModal() {
        /**
         * Crear modal de progreso dinámicamente
         */
        var modalHTML = '<div class="modal fade modal-auto-height" id="progressModal" data-bs-backdrop="static" data-bs-keyboard="false">' +
            '<div class="modal-dialog modal-lg">' +
                '<div class="modal-content">' +
                    '<div class="modal-header modal-header-app">' +
                        '<h5 class="modal-title"><i class="fas fa-cogs"></i> Restaurando Backup</h5>' +
                    '</div>' +
                    '<div class="modal-body modal-body-app">' +
                        '<div class="mb-3">' +
                            '<label class="form-label">Progreso:</label>' +
                            '<div class="progress">' +
                                '<div class="progress-bar progress-bar-striped progress-bar-animated" ' +
                                     'id="progressBar" style="width: 0%"></div>' +
                            '</div>' +
                            '<div class="text-center mt-1">' +
                                '<small id="progressPercent">0%</small>' +
                            '</div>' +
                        '</div>' +
                        '<div class="mb-3">' +
                            '<label class="form-label">Operación actual:</label>' +
                            '<div class="alert alert-info py-2" id="currentOperation">Iniciando...</div>' +
                        '</div>' +
                        '<div class="collapse" id="activityLogCollapse">' +
                            '<div class="border rounded p-2" style="max-height: 200px; overflow-y: auto;" id="activityLog"></div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="modal-footer modal-footer-app">' +
                        '<button type="button" class="btn btn-outline-secondary" data-bs-toggle="collapse" data-bs-target="#activityLogCollapse">' +
                            '<i class="fas fa-list"></i> Detalles' +
                        '</button>' +
                        '<button type="button" class="btn btn-warning" onclick="enhancedBackupManager.cancelOperation()" disabled>' +
                            '<i class="fas fa-stop"></i> Cancelar' +
                        '</button>' +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>';
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.progressModal = document.getElementById('progressModal');
        
        console.log('✅ [EnhancedBackupManager] Modal de progreso creado');
    }
    
    addToActivityLog(message) {
        /**
         * Agregar mensaje al log de actividad
         */
        var activityLog = document.getElementById('activityLog');
        if (activityLog) {
            var timestamp = new Date().toLocaleTimeString();
            var logEntry = document.createElement('div');
            logEntry.className = 'mb-1';
            logEntry.innerHTML = '<span class="text-muted">[' + timestamp + ']</span> ' + message;
            activityLog.appendChild(logEntry);
            activityLog.scrollTop = activityLog.scrollHeight;
        }
    }
    
    async showConfirmDialog(title, message) {
        /**
         * Mostrar dialog de confirmación usando el sistema del API Client
         */
        try {
            // Usar el sistema de confirmación del API Client
            if (window.confirm && typeof window.confirm.confirm === 'function') {
                console.log('🔍 [showConfirmDialog] Usando ConfirmDialog personalizado');
                return await window.confirm.confirm(message, title);
            } else {
                console.log('🔍 [showConfirmDialog] Fallback a confirm nativo');
                // Fallback al confirm nativo si no está disponible
                return window.confirm(title + '\n\n' + message);
            }
        } catch (error) {
            console.error('❌ [showConfirmDialog] Error:', error);
            // Último recurso: confirm nativo
            return window.confirm(title + '\n\n' + message);
        }
    }
    
    showAlert(message, type) {
        /**
         * Mostrar alerta toast o similar
         */
        // Usar el sistema de toast del API client si está disponible
        if (window.toast && typeof window.toast[type] === 'function') {
            window.toast[type](message);
        } else {
            // Fallback a alert nativo
            alert(message);
        }
    }
    
    createToast(message, type) {
        /**
         * Crear toast notification manualmente
         */
        var toastHTML = '<div class="toast align-items-center text-white bg-' + type + ' border-0" role="alert">' +
            '<div class="d-flex">' +
                '<div class="toast-body">' + message + '</div>' +
                '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
            '</div>' +
        '</div>';
        
        var toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        var toastElement = toastContainer.lastElementChild;
        var toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remover después de mostrar
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }
    
    async loadBackups() {
        /**
         * Cargar lista de backups desde el servidor
         */
        try {
            console.log('📋 [EnhancedBackupManager] Cargando lista de backups...');
            console.trace('🔍 [DEBUG] Stack trace de quién llama loadBackups():');
            
            // ⚠️ PROTECCIÓN: Evitar llamadas múltiples simultáneas
            if (this.loadingBackups) {
                console.warn('⚠️ [EnhancedBackupManager] Ya se está cargando la lista. Omitiendo...');
                return;
            }
            
            this.loadingBackups = true;
            
            var response = await fetch('/admin/backup/list');
            var data = await response.json();
            
            if (data.success) {
                this.renderBackupsList(data.backups);
                console.log('✅ [EnhancedBackupManager] ' + data.backups.length + ' backups cargados');
            } else {
                console.error('❌ [EnhancedBackupManager] Error cargando backups:', data.message);
                this.showAlert('Error cargando backups: ' + data.message, 'error');
            }
            
        } catch (error) {
            console.error('❌ [EnhancedBackupManager] Error en loadBackups:', error);
            this.showAlert('Error de conexión al cargar backups', 'error');
        } finally {
            // ✅ PROTECCIÓN: Liberar flag de carga
            this.loadingBackups = false;
        }
    }
    
    renderBackupsList(backups) {
        /**
         * Renderizar lista de backups en formato de tabla (grilla)
         */
        if (!this.elements.backupsList) {
            console.error('❌ [EnhancedBackupManager] Elemento backupsList no disponible');
            return;
        }
        
        if (backups.length === 0) {
            this.elements.backupsList.innerHTML = 
                '<tr>' +
                    '<td colspan="5" class="text-center py-4">' +
                        '<i class="fas fa-folder-open fa-3x text-muted mb-3"></i>' +
                        '<h5 class="text-muted">No hay backups disponibles</h5>' +
                        '<p class="text-muted mb-0">Cree un backup para comenzar</p>' +
                    '</td>' +
                '</tr>';
            return;
        }
        
        var html = '';
        for (var i = 0; i < backups.length; i++) {
            html += this.renderBackupRow(backups[i]);
        }
        
        this.elements.backupsList.innerHTML = html;
        console.log('📋 [EnhancedBackupManager] Lista renderizada: ' + backups.length + ' items');
    }
    
    renderBackupRow(backup) {
        /**
         * Renderizar fila individual de backup en la tabla
         */
        var statusIcon = backup.status === 'success' ? 
            '<i class="fas fa-check-circle text-success"></i> Exitoso' : 
            '<i class="fas fa-exclamation-circle text-warning"></i> Disponible';
            
        return '<tr>' +
            '<td>' +
                '<div class="d-flex align-items-center">' +
                    '<i class="fas fa-database text-primary me-2"></i>' +
                    '<div>' +
                        '<span class="fw-bold">' + backup.filename + '</span>' +
                        (backup.description ? '<br><small class="text-muted">' + backup.description + '</small>' : '') +
                    '</div>' +
                '</div>' +
            '</td>' +
            '<td>' +
                '<span class="text-nowrap">' + backup.date_formatted + '</span>' +
            '</td>' +
            '<td>' +
                '<span class="badge bg-info">' + backup.size_formatted + '</span>' +
            '</td>' +
            '<td>' +
                statusIcon +
            '</td>' +
            '<td class="text-end">' +
                '<div class="btn-group" role="group">' +
                    '<button class="btn btn-warning btn-sm" ' +
                            'onclick="enhancedBackupManager.showRestoreOptions(\'' + backup.filename + '\')" ' +
                            'title="Restaurar backup">' +
                        '<i class="fas fa-undo"></i>' +
                    '</button>' +
                    '<button class="btn btn-primary btn-sm" ' +
                            'onclick="window.open(\'/admin/backup/download/' + backup.filename + '\', \'_blank\')" ' +
                            'title="Descargar backup">' +
                        '<i class="fas fa-download"></i>' +
                    '</button>' +
                    '<button class="btn btn-danger btn-sm" ' +
                            'onclick="enhancedBackupManager.deleteBackup(\'' + backup.filename + '\')" ' +
                            'title="Eliminar backup">' +
                        '<i class="fas fa-trash"></i>' +
                    '</button>' +
                '</div>' +
            '</td>' +
        '</tr>';
    }
    
    async loadSystemStatus() {
        /**
         * Cargar estado del sistema
         */
        try {
            console.log('🖥️ [EnhancedBackupManager] Cargando estado del sistema...');
            
            var response = await fetch('/admin/backup/system-status');
            var data = await response.json();
            
            if (data.success) {
                console.log('✅ [EnhancedBackupManager] Estado del sistema obtenido:', data.system_status);
            }
            
        } catch (error) {
            console.warn('⚠️ [EnhancedBackupManager] Error obteniendo estado del sistema:', error);
        }
    }
    
    bindEvents() {
        /**
         * Vincular eventos de la interfaz
         */
        console.log('🔗 [EnhancedBackupManager] Vinculando eventos...');
        
        console.log('✅ [EnhancedBackupManager] Eventos vinculados');
    }
    
    cancelOperation() {
        /**
         * Cancelar operación actual (en desarrollo)
         */
        console.log('🛑 [EnhancedBackupManager] Cancelación de operación (función en desarrollo)');
        this.showAlert('Función de cancelación en desarrollo', 'warning');
    }
    
    async deleteBackup(filename) {
        /**
         * Eliminar backup específico
         */
        try {
            console.log('🗑️ [EnhancedBackupManager] Iniciando eliminación de backup: ' + filename);
            
            // Confirmar eliminación usando el sistema del API Client
            var confirmed = await this.showConfirmDialog(
                'Confirmar Eliminación',
                '¿Está seguro de que desea eliminar el backup "' + filename + '"?\n\nEsta acción no se puede deshacer.'
            );
            
            if (!confirmed) {
                console.log('ℹ️ [EnhancedBackupManager] Eliminación cancelada por el usuario');
                return;
            }
            
            // Realizar eliminación
            var response = await fetch('/admin/backup/delete/' + filename, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                }
            });
            
            var result = await response.json();
            
            if (result.success) {
                this.showAlert('Backup "' + filename + '" eliminado exitosamente', 'success');
                // Recargar lista de backups
                this.loadBackups();
            } else {
                this.showAlert('Error al eliminar backup: ' + result.message, 'error');
            }
            
        } catch (error) {
            console.error('❌ [EnhancedBackupManager] Error en eliminación:', error);
            this.showAlert('Error de conexión durante la eliminación', 'error');
        }
    }
    
    async debugDatabaseStatus(moment) {
        /**
         * Debug: Verificar estado actual de la base de datos
         */
        try {
            console.log('🔍 [Debug] Consultando estado de BD ' + moment + '...');
            
            var response = await fetch('/admin/backup/debug/db-status');
            var data = await response.json();
            
            if (data.success) {
                var status = data.database_status;
                console.log('📊 [Debug BD ' + moment + '] Total tablas: ' + status.total_tables);
                console.log('📊 [Debug BD ' + moment + '] Tablas principales:', status.main_tables);
                console.log('📊 [Debug BD ' + moment + '] Últimas actualizaciones:', status.recent_updates);
                
                // Mostrar en la consola del navegador para fácil visualización
                console.table(status.main_tables);
                
                return status;
            } else {
                console.error('❌ [Debug BD ' + moment + '] Error:', data.message);
                return null;
            }
            
        } catch (error) {
            console.error('❌ [Debug BD ' + moment + '] Error de conexión:', error);
            return null;
        }
    }
    
    showRestoreOptions(filename) {
        /**
         * Muestra un modal con opciones de restauración
         * @param {string} filename - Archivo de backup a restaurar
         */
        console.log(`🔄 [showRestoreOptions] Mostrando opciones para: ${filename}`);
        
        // Crear modal dinámicamente con estructura corregida
        const modalHtml = `
            <div class="modal fade modal-app modal-auto-height" id="restoreOptionsModal" tabindex="-1" aria-labelledby="restoreOptionsModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-size-medium">
                    <div class="modal-content">
                        <div class="modal-header modal-header-app">
                            <h5 class="modal-title" id="restoreOptionsModalLabel">
                                <i class="fas fa-undo"></i> Opciones de Restauración
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body modal-body-app">
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle"></i>
                                <strong>Archivo a restaurar:</strong> <code>${filename}</code>
                            </div>
                            
                            <h6><i class="fas fa-cog"></i> Tipo de Restauración:</h6>
                            
                            <div class="form-check mb-3">
                                <input class="form-check-input" type="radio" name="restoreType" id="restoreAdditive" value="additive" checked>
                                <label class="form-check-label" for="restoreAdditive">
                                    <strong>🔄 Restauración Aditiva</strong>
                                    <br>
                                    <small class="text-muted">Agrega los datos del backup a los datos existentes. Los datos actuales se conservan.</small>
                                </label>
                            </div>
                            
                            <div class="form-check mb-3">
                                <input class="form-check-input" type="radio" name="restoreType" id="restoreComplete" value="complete">
                                <label class="form-check-label" for="restoreComplete">
                                    <strong>🧹 Restauración Completa (Inteligente)</strong>
                                    <br>
                                    <small class="text-muted">Limpia datos existentes y restaura el backup. <strong>Preserva usuarios SUPERADMIN y tu sesión actual.</strong> <span class="text-warning">Operación parcialmente destructiva.</span></small>
                                </label>
                            </div>
                            
                            <div class="alert alert-info" id="completeRestoreWarning" style="display: none;">
                                <i class="fas fa-info-circle"></i>
                                <strong>ℹ️ Restauración Inteligente:</strong> El sistema limpiará todas las tablas de datos pero preservará automáticamente:
                                <ul class="mb-0 mt-2">
                                    <li>👤 <strong>Usuarios SUPERADMIN</strong> del sistema</li>
                                    <li>🔐 <strong>Tu sesión actual</strong> para mantener acceso</li>
                                    <li>⚙️ <strong>Configuración crítica</strong> del sistema</li>
                                </ul>
                            </div>
                        </div>
                        <div class="modal-footer modal-footer-app">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times"></i> Cancelar
                            </button>
                            <button type="button" class="btn btn-primary" id="btnExecuteRestore">
                                <i class="fas fa-undo"></i> Restaurar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Eliminar modal existente si hay uno
        const existingModal = document.getElementById('restoreOptionsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Agregar modal al DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Configurar eventos
        const restoreTypeRadios = document.querySelectorAll('input[name="restoreType"]');
        const completeRestoreWarning = document.getElementById('completeRestoreWarning');
        const btnExecuteRestore = document.getElementById('btnExecuteRestore');
        
        // Manejar cambios en tipo de restauración
        restoreTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'complete') {
                    completeRestoreWarning.style.display = 'block';
                } else {
                    completeRestoreWarning.style.display = 'none';
                }
            });
        });
        
        // Manejar click en botón restaurar
        btnExecuteRestore.addEventListener('click', () => {
            const selectedType = document.querySelector('input[name="restoreType"]:checked')?.value || 'additive';
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('restoreOptionsModal'));
            modal.hide();
            
            // Ejecutar restauración con tipo seleccionado
            this.executeRestore(filename, selectedType === 'complete');
        });
        
        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('restoreOptionsModal'));
        modal.show();
        
        // Cleanup cuando se cierre
        document.getElementById('restoreOptionsModal').addEventListener('hidden.bs.modal', function () {
            this.remove();
        });
    }
    
    executeRestore(filename, cleanDatabase = false) {
        /**
         * Ejecuta la restauración con las opciones seleccionadas
         * @param {string} filename - Archivo de backup a restaurar
         * @param {boolean} cleanDatabase - Si hacer limpieza completa de la BD
         */
        console.log(`🔄 [executeRestore] Ejecutando restauración: ${filename}, limpieza: ${cleanDatabase}`);
        
        // Ejecutar restauración
        this.restoreBackup(filename, cleanDatabase);
    }
}

// ⚠️ PROTECCIÓN GLOBAL: Evitar múltiples instancias
if (window.ENHANCED_BACKUP_MANAGER_INITIALIZED) {
    console.warn('⚠️ [GLOBAL] EnhancedBackupManager ya inicializado. Evitando duplicación.');
    // No hacer nada - reutilizar la instancia existente
} else {
    // Inicializar automáticamente cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🌐 [DOM] DOM cargado, inicializando EnhancedBackupManager...');
        
        // ⚠️ PROTECCIÓN: Marcar como inicializado
        window.ENHANCED_BACKUP_MANAGER_INITIALIZED = true;
        
        // ⚠️ PROTECCIÓN: Limpiar instancia anterior si existe
        if (window.enhancedBackupManager) {
            console.warn('⚠️ [EnhancedBackupManager] Limpiando instancia anterior...');
            
            try {
                if (window.enhancedBackupManager.progressInterval) {
                    clearInterval(window.enhancedBackupManager.progressInterval);
                }
                window.enhancedBackupManager.loadingBackups = false;
                window.enhancedBackupManager.isOperationActive = false;
            } catch (e) {
                console.warn('⚠️ [EnhancedBackupManager] Error limpiando instancia anterior:', e);
            }
        }
        
        // Crear instancia global ÚNICA
        window.enhancedBackupManager = new EnhancedBackupManager();
        
        console.log('✅ [EnhancedBackupManager] Manager mejorado listo (INSTANCIA ÚNICA)');
    });
}