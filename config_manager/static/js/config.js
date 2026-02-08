/**
 * Configuration Manager - Client-side JavaScript
 */

// Show loading modal
function showLoading(text = 'Đang xử lý...') {
    document.getElementById('loadingText').textContent = text;
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
}

// Hide loading modal
function hideLoading() {
    const loadingModal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (loadingModal) {
        loadingModal.hide();
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="bi bi-${type === 'danger' ? 'exclamation-triangle-fill' : 
                            type === 'success' ? 'check-circle-fill' : 
                            type === 'warning' ? 'exclamation-circle-fill' : 
                            'info-circle-fill'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container.mt-3');
    if (container) {
        container.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alerts = container.querySelectorAll('.alert');
            if (alerts.length > 0) {
                const lastAlert = alerts[alerts.length - 1];
                const bsAlert = new bootstrap.Alert(lastAlert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Form submission confirmation
document.addEventListener('DOMContentLoaded', function() {
    const configForm = document.getElementById('configForm');
    const saveBtn = document.getElementById('saveBtn');
    const resetBtn = document.getElementById('resetBtn');
    const restartBtn = document.getElementById('restartBtn');
    
    // Confirm before saving configuration
    if (configForm && saveBtn) {
        configForm.addEventListener('submit', function(e) {
            if (!confirm('Bạn có chắc chắn muốn lưu cấu hình này? File .env hiện tại sẽ được sao lưu tự động.')) {
                e.preventDefault();
                return false;
            }
            
            showLoading('Đang lưu cấu hình...');
        });
    }
    
    // Reset form
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('Bạn có chắc chắn muốn làm mới form? Các thay đổi chưa lưu sẽ bị mất.')) {
                window.location.reload();
            }
        });
    }
    
    // Restart service
    if (restartBtn) {
        restartBtn.addEventListener('click', function() {
            if (!confirm('Bạn có chắc chắn muốn khởi động lại dịch vụ? Điều này có thể gây gián đoạn hoạt động.')) {
                return;
            }
            
            showLoading('Đang khởi động lại dịch vụ...');
            
            fetch('/admin/restart-service', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                hideLoading();
                if (data.success) {
                    showAlert(data.message, 'success');
                } else {
                    showAlert('Lỗi: ' + data.error, 'danger');
                }
            })
            .catch(error => {
                hideLoading();
                showAlert('Lỗi kết nối: ' + error.message, 'danger');
            });
        });
    }
    
    // Load backups when modal is opened
    const backupModal = document.getElementById('backupModal');
    if (backupModal) {
        backupModal.addEventListener('show.bs.modal', function() {
            loadBackups();
        });
    }
});

// Load backup list
function loadBackups() {
    const backupList = document.getElementById('backupList');
    backupList.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Đang tải...</span>
            </div>
        </div>
    `;
    
    fetch('/admin/backups')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.backups.length > 0) {
                let html = '<div class="list-group">';
                data.backups.forEach(backup => {
                    const date = new Date(backup.modified);
                    const dateStr = date.toLocaleString('vi-VN');
                    const sizeKB = (backup.size / 1024).toFixed(2);
                    
                    html += `
                        <div class="backup-item">
                            <div class="backup-info">
                                <div>
                                    <div class="backup-name">
                                        <i class="bi bi-file-earmark-text"></i> ${backup.name}
                                    </div>
                                    <div class="backup-meta">
                                        <i class="bi bi-calendar"></i> ${dateStr} | 
                                        <i class="bi bi-hdd"></i> ${sizeKB} KB
                                    </div>
                                </div>
                                <button class="btn btn-sm btn-primary" onclick="restoreBackup('${backup.name}')">
                                    <i class="bi bi-arrow-counterclockwise"></i> Khôi phục
                                </button>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                backupList.innerHTML = html;
            } else {
                backupList.innerHTML = `
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle"></i> Không có bản sao lưu nào.
                    </div>
                `;
            }
        })
        .catch(error => {
            backupList.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> Lỗi khi tải danh sách sao lưu: ${error.message}
                </div>
            `;
        });
}

// Restore from backup
function restoreBackup(backupName) {
    if (!confirm(`Bạn có chắc chắn muốn khôi phục từ "${backupName}"? File .env hiện tại sẽ được sao lưu trước khi khôi phục.`)) {
        return;
    }
    
    showLoading('Đang khôi phục từ sao lưu...');
    
    fetch('/admin/restore', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ backup_name: backupName })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showAlert(data.message, 'success');
            // Close modal and reload page
            const modal = bootstrap.Modal.getInstance(document.getElementById('backupModal'));
            if (modal) {
                modal.hide();
            }
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showAlert('Lỗi: ' + data.error, 'danger');
        }
    })
    .catch(error => {
        hideLoading();
        showAlert('Lỗi kết nối: ' + error.message, 'danger');
    });
}

// Client-side validation
function validateForm() {
    let isValid = true;
    const errors = [];
    
    // Validate email
    const fbEmail = document.querySelector('input[name="fb_email"]');
    if (fbEmail && fbEmail.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(fbEmail.value)) {
            errors.push('Email Facebook không hợp lệ');
            isValid = false;
        }
    }
    
    // Validate proxy port
    const proxyPort = document.querySelector('input[name="proxy_port"]');
    if (proxyPort && proxyPort.value) {
        const port = parseInt(proxyPort.value);
        if (isNaN(port) || port < 1 || port > 65535) {
            errors.push('Cổng proxy phải từ 1 đến 65535');
            isValid = false;
        }
    }
    
    // Validate redirect URI
    const redirectUri = document.querySelector('input[name="facebook_redirect_uri"]');
    if (redirectUri && redirectUri.value) {
        const urlRegex = /^https?:\/\/.+/;
        if (!urlRegex.test(redirectUri.value)) {
            errors.push('URL callback phải bắt đầu với http:// hoặc https://');
            isValid = false;
        }
    }
    
    // Show errors
    if (!isValid) {
        errors.forEach(error => {
            showAlert(error, 'danger');
        });
    }
    
    return isValid;
}

// Add real-time validation
document.addEventListener('DOMContentLoaded', function() {
    const fbEmail = document.querySelector('input[name="fb_email"]');
    if (fbEmail) {
        fbEmail.addEventListener('blur', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
                if (this.value) {
                    this.classList.add('is-valid');
                }
            }
        });
    }
    
    const proxyPort = document.querySelector('input[name="proxy_port"]');
    if (proxyPort) {
        proxyPort.addEventListener('blur', function() {
            if (this.value) {
                const port = parseInt(this.value);
                if (isNaN(port) || port < 1 || port > 65535) {
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            } else {
                this.classList.remove('is-invalid', 'is-valid');
            }
        });
    }
});

// Prevent accidental page close with unsaved changes
let formChanged = false;
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('configForm');
    if (form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                formChanged = true;
            });
        });
        
        form.addEventListener('submit', function() {
            formChanged = false;
        });
    }
});

window.addEventListener('beforeunload', function(e) {
    if (formChanged) {
        e.preventDefault();
        e.returnValue = '';
    }
});
