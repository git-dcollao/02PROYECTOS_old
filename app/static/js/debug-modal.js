console.log('🔍 [DEBUG] Verificando estructura del modal de restauración');

// Verificar que el enhanced-backup-manager esté disponible
if (typeof enhancedBackupManager !== 'undefined') {
    console.log('✅ enhancedBackupManager disponible');
    
    // Simular apertura del modal de restauración
    enhancedBackupManager.showRestoreOptions('test_backup.sql.gz');
    
    // Verificar estructura del modal después de 1 segundo
    setTimeout(() => {
        const modal = document.getElementById('restoreOptionsModal');
        
        if (modal) {
            console.log('✅ Modal encontrado:', modal);
            
            // Verificar elementos clave
            const modalDialog = modal.querySelector('.modal-dialog');
            const modalContent = modal.querySelector('.modal-content');
            const modalHeader = modal.querySelector('.modal-header');
            const modalBody = modal.querySelector('.modal-body');
            const modalFooter = modal.querySelector('.modal-footer');
            const buttons = modal.querySelectorAll('.modal-footer .btn');
            
            console.log('📋 Estructura del modal:');
            console.log('  - modal-dialog:', modalDialog ? '✅' : '❌');
            console.log('  - modal-content:', modalContent ? '✅' : '❌');
            console.log('  - modal-header:', modalHeader ? '✅' : '❌');
            console.log('  - modal-body:', modalBody ? '✅' : '❌');
            console.log('  - modal-footer:', modalFooter ? '✅' : '❌');
            console.log('  - botones:', buttons.length, 'encontrados');
            
            // Verificar posición de botones
            if (modalFooter && buttons.length > 0) {
                const footerRect = modalFooter.getBoundingClientRect();
                console.log('📐 Posición del footer:', {
                    top: footerRect.top,
                    left: footerRect.left,
                    width: footerRect.width,
                    height: footerRect.height
                });
                
                buttons.forEach((btn, index) => {
                    const btnRect = btn.getBoundingClientRect();
                    console.log(`  Botón ${index + 1}:`, {
                        top: btnRect.top,
                        left: btnRect.left,
                        width: btnRect.width,
                        height: btnRect.height,
                        text: btn.textContent.trim()
                    });
                });
            }
            
        } else {
            console.log('❌ Modal no encontrado en el DOM');
        }
        
    }, 1000);
    
} else {
    console.log('❌ enhancedBackupManager no disponible');
}