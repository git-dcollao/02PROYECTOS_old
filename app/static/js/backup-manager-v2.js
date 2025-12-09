/**
 * Backup Manager V2 - JavaScript Refactorizado
 * =============================================
 * Sistema completo de gestión de backups con funcionalidades enterprise
 * 
 * Características:
 * ✅ Crear/Restaurar/Eliminar backups
 * ✅ Progress tracking en tiempo real
 * ✅ Drag & drop para uploads
 * ✅ Confirmaciones de seguridad
 * ✅ Paginación (10 por página)
 * ✅ Sistema de notificaciones
 * ✅ Manejo robusto de errores
 */

class BackupManagerV2 {
    constructor() {
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.backups = [];
        this.filteredBackups = [];
        this.selectedFile = null;
        this.progressInterval = null;
        this.startTime = null;
        
        this.init();
    }

    // ==========================================
    // INICIALIZACIÓN
    // ==========================================
    
    init() {
        console.log('🚀 [BackupManager V2] Inicializando...');
        
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.loadInitialData();
        
        console.log('✅ [BackupManager V2] Listo');
    }

    setupEventListeners() {
        console.log('🔧 [BackupManager V2] Configurando event listeners...');
        
        // Botones principales
        const btnCreateBackup = document.getElementById('btnCreateBackup');
        const btnUploadBackup = document.getElementById('btnUploadBackup');
        const btnRefresh = document.getElementById('btnRefresh');
        
        if (btnCreateBackup) {
            btnCreateBackup.addEventListener('click', () => this.showCreateBackupModal());
            console.log('✅ Listener: btnCreateBackup');
        } else {
            console.error('❌ No se encontró: btnCreateBackup');
        }
        
        if (btnUploadBackup) {
            btnUploadBackup.addEventListener('click', () => this.showUploadBackupModal());
            console.log('✅ Listener: btnUploadBackup');
        } else {
            console.error('❌ No se encontró: btnUploadBackup');
        }
        
        if (btnRefresh) {
            btnRefresh.addEventListener('click', () => this.loadBackups());
            console.log('✅ Listener: btnRefresh');
        } else {
            console.warn('⚠️ No se encontró: btnRefresh');
        }
        
        // Formularios
        const formCreateBackup = document.getElementById('formCreateBackup');
        const formRestoreConfirm = document.getElementById('formRestoreConfirm');
        
        if (formCreateBackup) {
            formCreateBackup.addEventListener('submit', (e) => this.handleCreateBackup(e));
            console.log('✅ Listener: formCreateBackup');
        }
        
        if (formRestoreConfirm) {
            formRestoreConfirm.addEventListener('submit', (e) => this.handleRestoreConfirm(e));
            console.log('✅ Listener: formRestoreConfirm');
        }
        
        // Búsqueda
        const searchBackup = document.getElementById('searchBackup');
        if (searchBackup) {
            searchBackup.addEventListener('input', (e) => this.handleSearch(e));
            console.log('✅ Listener: searchBackup');
        }
        
        // Selector de archivos
        const fileInput = document.getElementById('fileInput');
        const btnConfirmUpload = document.getElementById('btnConfirmUpload');
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
            console.log('✅ Listener: fileInput');
        }
        
        if (btnConfirmUpload) {
            btnConfirmUpload.addEventListener('click', () => this.handleFileUpload());
            console.log('✅ Listener: btnConfirmUpload');
        }
        
        // Validación de eliminación
        const deleteCodeInput = document.getElementById('deleteCodeInput');
        if (deleteCodeInput) {
            deleteCodeInput.addEventListener('input', (e) => this.validateDeleteCode(e));
            console.log('✅ Listener: deleteCodeInput');
        }
        
        // Validación de restauración
        const restoreConfirmText = document.getElementById('restoreConfirmText');
        const confirmConsequences = document.getElementById('confirmConsequences');
        const userPassword = document.getElementById('userPassword');
        
        if (restoreConfirmText) {
            restoreConfirmText.addEventListener('input', () => this.validateRestoreForm());
        }
        
        if (confirmConsequences) {
            confirmConsequences.addEventListener('change', () => this.validateRestoreForm());
        }
        
        if (userPassword) {
            userPassword.addEventListener('input', () => this.validateRestoreForm());
        }
        
        console.log('✅ [BackupManager V2] Event listeners configurados');
        
        // Agregar listener para limpiar estado cuando se cierra el modal de progreso
        const modalRestoreProgress = document.getElementById('modalRestoreProgress');
        if (modalRestoreProgress) {
            modalRestoreProgress.addEventListener('hidden.bs.modal', () => {
                console.log('🔄 Modal de progreso cerrado, limpiando estado...');
                if (this.progressInterval) {
                    clearInterval(this.progressInterval);
                    this.progressInterval = null;
                }
                this.errorCount = 0;
                this.resetProgressModal();
            });
        }
    }
    
    resetProgressModal() {
        // Resetear valores del modal a su estado inicial
        const progressBar = document.getElementById('progressBar');
        const progressPercent = document.getElementById('progressPercent');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) progressBar.style.width = '0%';
        if (progressPercent) progressPercent.textContent = '0%';
        if (progressText) progressText.textContent = '0%';
        
        if (document.getElementById('elapsedTime')) document.getElementById('elapsedTime').textContent = '00:00';
        if (document.getElementById('estimatedTime')) document.getElementById('estimatedTime').textContent = '--:--';
        if (document.getElementById('throughput')) document.getElementById('throughput').textContent = '0.0 stmt/s';
        
        if (document.getElementById('stmtExecuted')) document.getElementById('stmtExecuted').textContent = '0';
        if (document.getElementById('stmtSkipped')) document.getElementById('stmtSkipped').textContent = '0';
        if (document.getElementById('stmtTimeouts')) document.getElementById('stmtTimeouts').textContent = '0';
        if (document.getElementById('stmtRetries')) document.getElementById('stmtRetries').textContent = '0';
        
        const currentPhase = document.getElementById('currentPhase');
        if (currentPhase) {
            currentPhase.className = 'alert alert-info mb-0';
            currentPhase.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Iniciando...`;
        }
        
        // Resetear botones
        const btnCancel = document.getElementById('btnCancelRestore');
        const btnClose = document.getElementById('btnCloseProgress');
        if (btnCancel) btnCancel.style.display = 'inline-block';
        if (btnClose) btnClose.style.display = 'none';
    }

    setupDragAndDrop() {
        console.log('🎯 [BackupManager V2] Configurando drag & drop...');
        
        const uploadZone = document.getElementById('uploadZone');
        
        if (!uploadZone) {
            console.warn('⚠️ [BackupManager V2] uploadZone no encontrado, drag & drop deshabilitado');
            return;
        }
        
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });
        
        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });
        
        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.processFile(files[0]);
            }
        });
        
        console.log('✅ [BackupManager V2] Drag & drop configurado');
    }

    async loadInitialData() {
        await Promise.all([
            this.loadBackups(),
            this.loadSystemStatus()
        ]);
    }

    // ==========================================
    // CARGA DE DATOS
    // ==========================================
    
    async loadBackups() {
        try {
            console.log('📥 [BackupManager V2] Cargando lista de backups...');
            
            const response = await fetch('/admin/backup/list');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📊 [BackupManager V2] Respuesta recibida:', data);
            
            if (data.success) {
                this.backups = data.backups || [];
                this.filteredBackups = [...this.backups];
                this.renderBackups();
                this.updateStats(data.stats);
                console.log(`✅ [BackupManager V2] ${this.backups.length} backups cargados`);
            } else {
                throw new Error(data.message || 'Error al cargar backups');
            }
        } catch (error) {
            console.error('❌ [BackupManager V2] Error cargando backups:', error);
            this.showNotification('Error al cargar backups: ' + error.message, 'error');
            this.renderEmptyState('Error al cargar los datos. Por favor, recarga la página.');
        }
    }

    async loadSystemStatus() {
        try {
            console.log('🔍 [BackupManager V2] Cargando estado del sistema...');
            
            const response = await fetch('/admin/backup/system-status');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('📊 [BackupManager V2] Estado del sistema:', data);
            
            if (data.success && data.status) {
                const statusBadge = document.getElementById('dbStatus');
                if (statusBadge) {
                    statusBadge.textContent = data.status.database_status;
                    statusBadge.className = `badge ${data.status.database_status === 'Conectado' ? 'bg-success' : 'bg-danger'}`;
                    console.log('✅ [BackupManager V2] Estado DB actualizado:', data.status.database_status);
                }
            }
        } catch (error) {
            console.error('❌ [BackupManager V2] Error cargando estado del sistema:', error);
            const statusBadge = document.getElementById('dbStatus');
            if (statusBadge) {
                statusBadge.textContent = 'Error';
                statusBadge.className = 'badge bg-secondary';
            }
        }
    }

    // ==========================================
    // RENDERIZADO
    // ==========================================
    
    renderBackups() {
        const tbody = document.getElementById('backupsList');
        const start = (this.currentPage - 1) * this.itemsPerPage;
        const end = start + this.itemsPerPage;
        const pageBackups = this.filteredBackups.slice(start, end);
        
        if (pageBackups.length === 0) {
            this.renderEmptyState();
            return;
        }
        
        tbody.innerHTML = pageBackups.map(backup => this.createBackupRow(backup)).join('');
        this.renderPagination();
        this.updatePaginationInfo();
    }

    createBackupRow(backup) {
        const date = new Date(backup.created_at).toLocaleString('es-CL');
        const size = this.formatFileSize(backup.size);
        const statusClass = backup.status === 'success' ? 'success' : 'danger';
        const statusIcon = backup.status === 'success' ? 'check-circle' : 'exclamation-triangle';
        
        return `
            <tr class="fade-in">
                <td class="px-4 py-3">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-file-archive text-primary me-2"></i>
                        <div>
                            <strong>${backup.filename}</strong>
                            ${backup.description ? `<br><small class="text-muted">${backup.description}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td class="px-4 py-3">
                    <i class="fas fa-calendar-alt text-muted me-1"></i>
                    ${date}
                </td>
                <td class="px-4 py-3">
                    <span class="badge bg-secondary">${size}</span>
                </td>
                <td class="px-4 py-3">
                    <span class="badge bg-${statusClass}">
                        <i class="fas fa-${statusIcon}"></i> ${backup.status}
                    </span>
                </td>
                <td class="text-end px-4 py-3">
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-success" onclick="backupManager.restoreBackup('${backup.filename}')" title="Restaurar">
                            <i class="fas fa-sync-alt"></i> Restaurar
                        </button>
                        <button class="btn btn-outline-primary" onclick="backupManager.downloadBackup('${backup.filename}')" title="Descargar">
                            <i class="fas fa-download"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="backupManager.deleteBackup('${backup.filename}')" title="Eliminar">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    renderEmptyState(message = 'No hay backups disponibles') {
        const tbody = document.getElementById('backupsList');
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <p class="text-muted">${message}</p>
                    <button class="btn btn-primary" onclick="backupManager.showCreateBackupModal()">
                        <i class="fas fa-plus"></i> Crear tu primer backup
                    </button>
                </td>
            </tr>
        `;
        this.renderPagination();
        this.updatePaginationInfo();
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredBackups.length / this.itemsPerPage);
        const pagination = document.getElementById('paginationControls');
        
        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // Botón anterior
        html += `
            <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="backupManager.goToPage(${this.currentPage - 1}); return false;">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 1 && i <= this.currentPage + 1)) {
                html += `
                    <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="backupManager.goToPage(${i}); return false;">${i}</a>
                    </li>
                `;
            } else if (i === this.currentPage - 2 || i === this.currentPage + 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        // Botón siguiente
        html += `
            <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="backupManager.goToPage(${this.currentPage + 1}); return false;">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        pagination.innerHTML = html;
    }

    updatePaginationInfo() {
        const total = this.filteredBackups.length;
        const start = total > 0 ? (this.currentPage - 1) * this.itemsPerPage + 1 : 0;
        const end = Math.min(start + this.itemsPerPage - 1, total);
        
        document.getElementById('paginationInfo').textContent = `${start}-${end} de ${total}`;
    }

    updateStats(stats) {
        if (!stats) return;
        
        document.getElementById('totalBackups').textContent = stats.total_backups || 0;
        document.getElementById('lastBackupDate').textContent = stats.last_backup_date || '-';
        document.getElementById('totalSize').textContent = stats.total_size || '0 MB';
    }

    // ==========================================
    // CREAR BACKUP
    // ==========================================
    
    showCreateBackupModal() {
        const modal = new bootstrap.Modal(document.getElementById('modalCreateBackup'));
        modal.show();
    }

    async handleCreateBackup(e) {
        e.preventDefault();
        
        const name = document.getElementById('backupName').value.trim();
        const description = document.getElementById('backupDescription').value.trim();
        const includeData = document.getElementById('includeData').checked;
        const compress = document.getElementById('compressBackup').checked;
        
        const formData = new FormData();
        if (name) formData.append('name', name);
        if (description) formData.append('description', description);
        formData.append('include_data', includeData ? 'on' : 'off');
        formData.append('compress', compress ? 'on' : 'off');
        
        try {
            this.showLoading('Creando backup...');
            
            const response = await fetch('/admin/backup/create', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            this.hideLoading();
            
            if (data.success) {
                this.showNotification('Backup creado exitosamente', 'success');
                bootstrap.Modal.getInstance(document.getElementById('modalCreateBackup')).hide();
                document.getElementById('formCreateBackup').reset();
                await this.loadBackups();
            } else {
                throw new Error(data.message || 'Error al crear backup');
            }
        } catch (error) {
            this.hideLoading();
            console.error('❌ Error creando backup:', error);
            this.showNotification(error.message, 'error');
        }
    }

    // ==========================================
    // RESTAURAR BACKUP
    // ==========================================
    
    restoreBackup(filename) {
        document.getElementById('restoreBackupName').textContent = filename;
        document.getElementById('restoreBackupFilename').value = filename;
        
        const modal = new bootstrap.Modal(document.getElementById('modalRestoreConfirm'));
        modal.show();
    }

    async handleRestoreConfirm(e) {
        e.preventDefault();
        
        const filename = document.getElementById('restoreBackupFilename').value;
        const cleanDatabase = document.getElementById('cleanDatabase').checked;
        const password = document.getElementById('userPassword').value;
        
        // Cerrar modal de confirmación
        bootstrap.Modal.getInstance(document.getElementById('modalRestoreConfirm')).hide();
        
        // Mostrar modal de progreso
        const progressModal = new bootstrap.Modal(document.getElementById('modalRestoreProgress'));
        progressModal.show();
        
        try {
            this.startTime = Date.now();
            
            const response = await fetch('/admin/backup/restore-file', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    filename: filename,
                    clean_database: cleanDatabase,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Iniciar polling de progreso
                this.startProgressTracking();
            } else {
                throw new Error(data.message || 'Error al iniciar restauración');
            }
        } catch (error) {
            console.error('❌ Error restaurando backup:', error);
            this.showNotification(error.message, 'error');
            bootstrap.Modal.getInstance(document.getElementById('modalRestoreProgress')).hide();
        }
    }

    startProgressTracking() {
        this.progressInterval = setInterval(() => {
            this.updateProgress();
        }, 2000); // Actualizar cada 2 segundos
    }

    async updateProgress() {
        try {
            const response = await fetch('/admin/backup/progress');
            const data = await response.json();
            
            // Si no hay progreso activo, detener polling
            if (!data.success || !data.progress) {
                console.log('⚠️ No hay progreso activo, deteniendo polling');
                clearInterval(this.progressInterval);
                // Cerrar modal automáticamente si no hay tarea activa
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalRestoreProgress'));
                if (modal) {
                    modal.hide();
                }
                return;
            }
            
            const progress = data.progress;
            
            // CRÍTICO: Verificar si la operación sigue activa
            if (progress.is_active === false) {
                console.log('✅ Operación completada (is_active: false), cerrando modal...');
                clearInterval(this.progressInterval);
                this.progressInterval = null;
                
                // Si llegó a 100%, mostrar mensaje de éxito y cerrar
                if (progress.progress_percent >= 100) {
                    this.showCompletionMessage(progress);
                } else {
                    // Cerrar directamente si no llegó a 100%
                    const modal = bootstrap.Modal.getInstance(document.getElementById('modalRestoreProgress'));
                    if (modal) {
                        modal.hide();
                    }
                }
                return;
            }
            
            // Actualizar barra de progreso
            const progressBar = document.getElementById('progressBar');
            const progressPercent = document.getElementById('progressPercent');
            const progressText = document.getElementById('progressText');
            
            // CORRECCIÓN: usar progress_percent del backend
            const percentage = progress.progress_percent || 0;
            progressBar.style.width = `${percentage}%`;
            progressPercent.textContent = `${percentage}%`;
            progressText.textContent = `${percentage}%`;
            
            // Actualizar tiempos
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            document.getElementById('elapsedTime').textContent = this.formatTime(elapsed);
            
            if (percentage > 0 && percentage < 100) {
                const estimated = Math.floor((elapsed / percentage) * (100 - percentage));
                document.getElementById('estimatedTime').textContent = this.formatTime(estimated);
            } else if (percentage >= 100) {
                document.getElementById('estimatedTime').textContent = '00:00';
            }
            
            // Actualizar estadísticas
            if (progress.details) {
                document.getElementById('stmtExecuted').textContent = progress.details.executed || 0;
                document.getElementById('stmtSkipped').textContent = progress.details.skipped || 0;
                document.getElementById('stmtTimeouts').textContent = progress.details.timeouts || 0;
                document.getElementById('stmtRetries').textContent = progress.details.retries || 0;
            }
            
            // Actualizar fase actual
            const currentPhaseDiv = document.getElementById('currentPhase');
            // CORRECCIÓN: usar current_operation del backend
            const message = progress.current_operation || 'Procesando...';
            currentPhaseDiv.innerHTML = `
                <i class="fas fa-${percentage === 100 ? 'check' : 'spinner fa-spin'}"></i> 
                ${message}
            `;
            
            // Calcular throughput
            if (progress.details && progress.details.executed > 0 && elapsed > 0) {
                const throughput = (progress.details.executed / elapsed).toFixed(1);
                document.getElementById('throughput').textContent = `${throughput} stmt/s`;
            } else {
                // Mostrar 0 si no hay datos
                document.getElementById('throughput').textContent = '0.0 stmt/s';
            }
            
            // Si completó, detener polling y mostrar mensaje
            if (percentage >= 100) {
                console.log('✅ Restauración completada (100%), deteniendo polling');
                clearInterval(this.progressInterval);
                this.progressInterval = null;
                this.showCompletionMessage(progress);
            }
        } catch (error) {
            console.error('❌ Error obteniendo progreso:', error);
            // En caso de error, detener polling después de varios intentos
            if (!this.errorCount) this.errorCount = 0;
            this.errorCount++;
            if (this.errorCount > 5) {
                console.log('⚠️ Demasiados errores, deteniendo polling');
                clearInterval(this.progressInterval);
            }
        }
    }

    showCompletionMessage(progress) {
        // Mostrar botón de cerrar, ocultar botón de cancelar
        const btnCancel = document.getElementById('btnCancelRestore');
        const btnClose = document.getElementById('btnCloseProgress');
        
        if (btnCancel) btnCancel.style.display = 'none';
        if (btnClose) btnClose.style.display = 'inline-block';
        
        const phaseDiv = document.getElementById('currentPhase');
        
        if (progress.success !== false) { // Si es true o undefined (completado sin error explícito)
            phaseDiv.className = 'alert alert-success mb-0';
            phaseDiv.innerHTML = `
                <i class="fas fa-check-circle"></i> 
                <strong>¡Restauración completada exitosamente!</strong><br>
                <small class="text-muted">Redirigiendo al login en 3 segundos...</small>
            `;
            this.showNotification('Backup restaurado correctamente - Volviendo al login...', 'success');
            
            // Cerrar modal y redirigir al login después de 3 segundos
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalRestoreProgress'));
                if (modal) {
                    modal.hide();
                    console.log('✅ Modal cerrado - Redirigiendo al login');
                }
                
                // Redirigir al login para forzar nueva sesión
                window.location.href = '/auth/logout?next=/auth/login';
            }, 3000);
        } else {
            phaseDiv.className = 'alert alert-danger mb-0';
            phaseDiv.innerHTML = `
                <i class="fas fa-exclamation-circle"></i> 
                <strong>Error en la restauración</strong><br>
                ${progress.error_message || progress.message || 'Error desconocido'}
            `;
            this.showNotification('Error al restaurar backup', 'error');
        }
        
        // NO recargar backups aquí - el usuario será redirigido
    }

    // ==========================================
    // DESCARGAR BACKUP
    // ==========================================
    
    downloadBackup(filename) {
        window.location.href = `/admin/backup/download/${filename}`;
        this.showNotification('Descarga iniciada', 'info');
    }

    // ==========================================
    // ELIMINAR BACKUP
    // ==========================================
    
    deleteBackup(filename) {
        const code = this.generateDeleteCode();
        
        document.getElementById('deleteBackupName').textContent = filename;
        document.getElementById('deleteBackupFilename').value = filename;
        document.getElementById('deleteCode').textContent = code;
        document.getElementById('deleteGeneratedCode').value = code;
        document.getElementById('deleteCodeInput').value = '';
        document.getElementById('btnConfirmDelete').disabled = true;
        
        const modal = new bootstrap.Modal(document.getElementById('modalDeleteConfirm'));
        modal.show();
    }

    generateDeleteCode() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let code = '';
        for (let i = 0; i < 6; i++) {
            code += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return code;
    }

    validateDeleteCode(e) {
        const input = e.target.value.toUpperCase();
        const correctCode = document.getElementById('deleteGeneratedCode').value;
        const btn = document.getElementById('btnConfirmDelete');
        
        btn.disabled = input !== correctCode;
    }

    async confirmDelete() {
        const filename = document.getElementById('deleteBackupFilename').value;
        
        try {
            this.showLoading('Eliminando backup...');
            
            const response = await fetch(`/admin/backup/delete/${filename}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            const data = await response.json();
            
            this.hideLoading();
            
            if (data.success) {
                this.showNotification('Backup eliminado exitosamente', 'success');
                bootstrap.Modal.getInstance(document.getElementById('modalDeleteConfirm')).hide();
                await this.loadBackups();
            } else {
                throw new Error(data.message || 'Error al eliminar backup');
            }
        } catch (error) {
            this.hideLoading();
            console.error('❌ Error eliminando backup:', error);
            this.showNotification(error.message, 'error');
        }
    }

    // ==========================================
    // SUBIR BACKUP
    // ==========================================
    
    showUploadBackupModal() {
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('uploadProgress').style.display = 'none';
        document.getElementById('btnConfirmUpload').disabled = true;
        this.selectedFile = null;
        
        const modal = new bootstrap.Modal(document.getElementById('modalUploadBackup'));
        modal.show();
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // Validar extensión
        const validExtensions = ['.sql', '.gz', '.zip'];
        const isValid = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
        
        if (!isValid) {
            this.showNotification('Formato de archivo no válido', 'error');
            return;
        }
        
        this.selectedFile = file;
        
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);
        document.getElementById('fileInfo').style.display = 'block';
        document.getElementById('btnConfirmUpload').disabled = false;
    }

    async handleFileUpload() {
        if (!this.selectedFile) return;
        
        const formData = new FormData();
        formData.append('backup_file', this.selectedFile);
        
        try {
            const progressBar = document.getElementById('uploadProgress');
            const progressBarInner = progressBar.querySelector('.progress-bar');
            
            progressBar.style.display = 'block';
            document.getElementById('btnConfirmUpload').disabled = true;
            
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    progressBarInner.style.width = `${percent}%`;
                    progressBarInner.textContent = `${percent}%`;
                }
            });
            
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    const data = JSON.parse(xhr.responseText);
                    
                    if (data.success) {
                        this.showNotification('Archivo subido exitosamente', 'success');
                        bootstrap.Modal.getInstance(document.getElementById('modalUploadBackup')).hide();
                        this.loadBackups();
                    } else {
                        throw new Error(data.message || 'Error al subir archivo');
                    }
                } else {
                    throw new Error('Error en la petición');
                }
            });
            
            xhr.addEventListener('error', () => {
                throw new Error('Error de red al subir archivo');
            });
            
            xhr.open('POST', '/admin/backup/upload', true);
            xhr.setRequestHeader('X-CSRFToken', this.getCSRFToken());
            xhr.send(formData);
            
        } catch (error) {
            console.error('❌ Error subiendo archivo:', error);
            this.showNotification(error.message, 'error');
            document.getElementById('btnConfirmUpload').disabled = false;
        }
    }

    // ==========================================
    // BÚSQUEDA Y FILTROS
    // ==========================================
    
    handleSearch(e) {
        const query = e.target.value.toLowerCase();
        
        this.filteredBackups = this.backups.filter(backup => 
            backup.filename.toLowerCase().includes(query) ||
            (backup.description && backup.description.toLowerCase().includes(query))
        );
        
        this.currentPage = 1;
        this.renderBackups();
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.filteredBackups.length / this.itemsPerPage);
        
        if (page < 1 || page > totalPages) return;
        
        this.currentPage = page;
        this.renderBackups();
        
        // Scroll al inicio de la tabla
        document.getElementById('backupsTable').scrollIntoView({ behavior: 'smooth' });
    }

    // ==========================================
    // VALIDACIONES
    // ==========================================
    
    validateRestoreForm() {
        const text = document.getElementById('restoreConfirmText').value;
        const checkbox = document.getElementById('confirmConsequences').checked;
        const password = document.getElementById('userPassword').value;
        const btn = document.getElementById('btnConfirmRestore');
        
        const isValid = text === 'RESTAURAR' && checkbox && password.length >= 6;
        btn.disabled = !isValid;
    }

    // ==========================================
    // UTILIDADES
    // ==========================================
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    showLoading(message = 'Cargando...') {
        const overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <p class="mt-3 mb-0">${message}</p>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }

    showNotification(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        setTimeout(() => toast.remove(), 5000);
    }
}

// ==========================================
// INICIALIZACIÓN GLOBAL
// ==========================================
let backupManager;

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 [INIT] DOM Content Loaded - Inicializando sistema...');
    
    // 1. Crear instancia principal
    try {
        backupManager = new BackupManagerV2();
        console.log('✅ [INIT] BackupManagerV2 inicializado');
    } catch (error) {
        console.error('❌ [INIT] Error al inicializar BackupManagerV2:', error);
        return;
    }
    
    // 2. Agregar hidden inputs necesarios para los modales
    setupHiddenInputs();
    
    // 3. Configurar botón de confirmación de eliminación
    setupDeleteConfirmButton();
    
    console.log('✅ [INIT] Sistema completamente inicializado');
});

// Helper: Configurar inputs ocultos para modales
function setupHiddenInputs() {
    // Hidden input para restauración
    const formRestoreConfirm = document.getElementById('formRestoreConfirm');
    if (formRestoreConfirm && !formRestoreConfirm.querySelector('input[name="restoreBackupFilename"]')) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'restoreBackupFilename';
        formRestoreConfirm.appendChild(input);
        console.log('✅ [INIT] Hidden input para restauración agregado');
    }
    
    // Hidden inputs para eliminación
    const modalDeleteConfirm = document.getElementById('modalDeleteConfirm');
    if (modalDeleteConfirm && !modalDeleteConfirm.querySelector('input[name="deleteBackupFilename"]')) {
        const modalBody = modalDeleteConfirm.querySelector('.modal-body');
        
        if (modalBody) {
            const filenameInput = document.createElement('input');
            filenameInput.type = 'hidden';
            filenameInput.id = 'deleteBackupFilename';
            modalBody.appendChild(filenameInput);
            
            const codeInput = document.createElement('input');
            codeInput.type = 'hidden';
            codeInput.id = 'deleteGeneratedCode';
            modalBody.appendChild(codeInput);
            
            console.log('✅ [INIT] Hidden inputs para eliminación agregados');
        }
    }
}

// Helper: Configurar botón de confirmación de eliminación
function setupDeleteConfirmButton() {
    const btnConfirmDelete = document.getElementById('btnConfirmDelete');
    if (btnConfirmDelete && !btnConfirmDelete.hasAttribute('data-listener-attached')) {
        btnConfirmDelete.addEventListener('click', () => {
            if (backupManager) {
                backupManager.confirmDelete();
            }
        });
        btnConfirmDelete.setAttribute('data-listener-attached', 'true');
        console.log('✅ [INIT] Listener de confirmación de eliminación agregado');
    }
}
