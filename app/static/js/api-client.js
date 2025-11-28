/**
 * Cliente API Centralizado con CSRF Protection
 * 
 * Maneja todas las peticiones HTTP con:
 * - CSRF token automático
 * - Manejo de errores estandarizado
 * - Loading states
 * - Retry logic
 * 
 * @author Sistema de Gestión de Proyectos
 * @version 2.0.0
 */

class APIClient {
    constructor() {
        this.baseURL = window.location.origin;
        this.csrfToken = this.getCSRFToken();
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken
        };
    }

    /**
     * Obtener CSRF token desde meta tag o cookie
     */
    getCSRFToken() {
        // Intentar desde meta tag primero
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }

        // Intentar desde cookie
        const name = 'csrf_token=';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.indexOf(name) === 0) {
                return cookie.substring(name.length);
            }
        }

        console.warn('⚠️ CSRF token no encontrado. Las peticiones pueden fallar.');
        return '';
    }

    /**
     * Método HTTP genérico
     */
    async request(url, options = {}) {
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            credentials: 'include', // 🔥 CRÍTICO: Incluir cookies de sesión
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            // Manejar respuestas no-OK
            if (!response.ok) {
                // Intentar extraer mensaje de error del response
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    if (errorData.message || errorData.error) {
                        errorMessage = errorData.message || errorData.error;
                    }
                } catch (e) {
                    // Si no es JSON, usar el statusText
                }
                
                throw new Error(errorMessage);
            }

            // Retornar JSON parseado
            const data = await response.json();
            return data;

        } catch (error) {
            console.error('❌ Error en petición:', {
                url,
                method: config.method || 'GET',
                error: error.message
            });
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET'
        });
    }

    /**
     * POST request
     */
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            body: JSON.stringify(data)
        });
    }

    /**
     * Upload file (multipart/form-data)
     */
    async upload(endpoint, formData) {
        // No incluir Content-Type para que el navegador lo setee automáticamente con boundary
        const headers = {
            'X-CSRFToken': this.csrfToken
        };

        return this.request(endpoint, {
            method: 'POST',
            headers,
            body: formData
        });
    }
}

// Crear instancia global
window.api = new APIClient();

/**
 * Toast Notification System
 */
class ToastNotifier {
    constructor(containerId = 'toast-container') {
        this.container = document.getElementById(containerId);
        
        // Crear container si no existe
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = containerId;
            this.container.className = 'position-fixed top-0 end-0 p-3';
            this.container.style.zIndex = '9999';
            document.body.appendChild(this.container);
        }
    }

    /**
     * Mostrar notificación toast
     */
    show(message, type = 'info', duration = 3000) {
        const toastId = `toast-${Date.now()}`;
        
        // Mapear tipos a clases de Bootstrap
        const typeMap = {
            success: 'bg-success text-white',
            error: 'bg-danger text-white',
            warning: 'bg-warning text-dark',
            info: 'bg-info text-white'
        };

        const bgClass = typeMap[type] || typeMap.info;
        
        // Iconos para cada tipo
        const iconMap = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        const icon = iconMap[type] || iconMap.info;

        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas ${icon} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        this.container.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: duration
        });

        toast.show();

        // Eliminar del DOM después de ocultarse
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });

        return toast;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Crear instancia global
window.toast = new ToastNotifier();

/**
 * Loading Overlay System
 */
class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.overlayCreated = false;
    }

    createOverlay() {
        if (this.overlayCreated || document.getElementById('global-loading-overlay')) {
            return;
        }

        const overlay = document.createElement('div');
        overlay.id = 'global-loading-overlay';
        overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
        overlay.style.cssText = 'background: rgba(0,0,0,0.5); z-index: 99999; display: none;';
        overlay.innerHTML = `
            <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Cargando...</span>
            </div>
        `;
        document.body.appendChild(overlay);
        this.overlayCreated = true;
    }

    show(loaderId = 'default') {
        // Crear overlay solo cuando se necesita
        if (!this.overlayCreated) {
            this.createOverlay();
        }
        
        this.activeLoaders.add(loaderId);
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }

    hide(loaderId = 'default') {
        this.activeLoaders.delete(loaderId);
        
        // Solo ocultar si no hay más loaders activos
        if (this.activeLoaders.size === 0) {
            const overlay = document.getElementById('global-loading-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        }
    }

    hideAll() {
        this.activeLoaders.clear();
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
}

// Crear instancia global
window.loading = new LoadingManager();

/**
 * Confirmation Dialog System
 */
class ConfirmDialog {
    async confirm(message, title = 'Confirmar acción', options = {}) {
        return new Promise((resolve) => {
            const modalId = 'confirm-modal-' + Date.now();
            
            const modalHTML = `
                <div class="modal fade" id="${modalId}" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header ${options.headerClass || 'bg-primary text-white'}">
                                <h5 class="modal-title">
                                    <i class="fas ${options.icon || 'fa-question-circle'} me-2"></i>
                                    ${title}
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                ${message}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                    ${options.cancelText || 'Cancelar'}
                                </button>
                                <button type="button" class="btn ${options.confirmClass || 'btn-primary'}" id="confirm-btn-${modalId}">
                                    ${options.confirmText || 'Confirmar'}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', modalHTML);
            const modalElement = document.getElementById(modalId);
            const modal = new bootstrap.Modal(modalElement);

            document.getElementById(`confirm-btn-${modalId}`).addEventListener('click', () => {
                modal.hide();
                resolve(true);
            });

            modalElement.addEventListener('hidden.bs.modal', () => {
                modalElement.remove();
                resolve(false);
            });

            modal.show();
        });
    }

    async delete(itemName) {
        return this.confirm(
            `¿Está seguro de que desea eliminar <strong>"${itemName}"</strong>?<br><br>Esta acción no se puede deshacer.`,
            'Confirmar eliminación',
            {
                icon: 'fa-trash',
                headerClass: 'bg-danger text-white',
                confirmClass: 'btn-danger',
                confirmText: 'Eliminar'
            }
        );
    }
}

// Crear instancia global
window.confirm = new ConfirmDialog();

console.log('✅ API Client inicializado correctamente');
console.log('📡 Endpoints disponibles: api.get(), api.post(), api.put(), api.delete()');
console.log('🔔 Notificaciones: toast.success(), toast.error(), toast.warning(), toast.info()');
console.log('⏳ Loading: loading.show(), loading.hide()');
console.log('💬 Confirmación: confirm.confirm(), confirm.delete()');
