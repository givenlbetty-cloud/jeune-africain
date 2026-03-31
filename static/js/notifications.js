/**
 * PHASE 6: NOTIFICATIONS SYSTEM
 * Toast notifications, loading spinners, progress bars
 */

class NotificationSystem {
    constructor() {
        this.toastContainer = null;
        this.initContainer();
        this.loadingSpinner = null;
    }

    /**
     * Initialize toast container
     */
    initContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
            `;
            document.body.appendChild(container);
            this.toastContainer = container;
        }
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} type - 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms (default: 4000)
     */
    toast(message, type = 'info', duration = 4000) {
        const toastId = `toast-${Date.now()}`;
        
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        };

        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };

        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = 'alert alert-dismissible fade show';
        toast.setAttribute('role', 'alert');
        toast.style.cssText = `
            background-color: white;
            border-left: 4px solid ${colors[type]};
            margin-bottom: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
        `;

        toast.innerHTML = `
            <i class="${icons[type]}" style="color: ${colors[type]}; margin-right: 10px;"></i>
            <span>${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        this.toastContainer.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.remove();
        }, duration);

        return toastId;
    }

    /**
     * Show loading spinner
     * @param {string} message - Message to display
     * @returns {string} spinner ID
     */
    showLoading(message = 'Chargement...') {
        const spinnerId = `spinner-${Date.now()}`;
        
        const spinner = document.createElement('div');
        spinner.id = spinnerId;
        spinner.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px 40px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            z-index: 10000;
            text-align: center;
            min-width: 200px;
        `;

        spinner.innerHTML = `
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="visually-hidden">Chargement...</span>
            </div>
            <p class="text-muted mb-0">${message}</p>
        `;

        document.body.appendChild(spinner);
        this.loadingSpinner = spinner;

        return spinnerId;
    }

    /**
     * Hide loading spinner
     */
    hideLoading() {
        if (this.loadingSpinner) {
            this.loadingSpinner.remove();
            this.loadingSpinner = null;
        }
    }

    /**
     * Show progress bar
     * @param {string} title - Progress title
     * @returns {object} progress control object
     */
    showProgress(title = 'Progression') {
        const progressId = `progress-${Date.now()}`;
        
        const progressContainer = document.createElement('div');
        progressContainer.id = progressId;
        progressContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 15px 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 10000;
        `;

        progressContainer.innerHTML = `
            <div style="margin-bottom: 10px; font-weight: 500;">${title}</div>
            <div class="progress" style="height: 20px;">
                <div class="progress-bar bg-success" id="${progressId}-bar" role="progressbar" 
                     style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                    <span style="font-size: 12px; line-height: 20px;">0%</span>
                </div>
            </div>
        `;

        document.body.appendChild(progressContainer);

        return {
            update: (percentage) => {
                const bar = document.getElementById(`${progressId}-bar`);
                if (bar) {
                    bar.style.width = `${percentage}%`;
                    bar.setAttribute('aria-valuenow', percentage);
                    bar.innerHTML = `<span style="font-size: 12px; line-height: 20px;">${percentage}%</span>`;
                }
            },
            complete: () => {
                progressContainer.remove();
            }
        };
    }

    /**
     * Show confirmation dialog
     * @param {string} title - Dialog title
     * @param {string} message - Dialog message
     * @param {string} confirmText - Confirm button text
     * @param {string} cancelText - Cancel button text
     * @returns {Promise} resolves to true/false
     */
    confirm(title, message, confirmText = 'Confirmer', cancelText = 'Annuler') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.style.cssText = 'display: block; background: rgba(0,0,0,0.5);';
            modal.setAttribute('role', 'dialog');

            modal.innerHTML = `
                <div class="modal-dialog" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary cancel-btn">${cancelText}</button>
                            <button type="button" class="btn btn-primary confirm-btn">${confirmText}</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            const confirmBtn = modal.querySelector('.confirm-btn');
            const cancelBtn = modal.querySelector('.cancel-btn');
            const closeBtn = modal.querySelector('.btn-close');

            confirmBtn.addEventListener('click', () => {
                modal.remove();
                resolve(true);
            });

            cancelBtn.addEventListener('click', () => {
                modal.remove();
                resolve(false);
            });

            closeBtn.addEventListener('click', () => {
                modal.remove();
                resolve(false);
            });

            // Click outside to cancel
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve(false);
                }
            });
        });
    }

    /**
     * Show error notification with details
     * @param {string} title - Error title
     * @param {string} message - Error message
     * @param {string} details - Optional error details
     */
    error(title, message, details = null) {
        let fullMessage = message;
        if (details) {
            fullMessage += `\n\n${details}`;
        }

        this.toast(`${title}: ${message}`, 'error', 5000);

        if (details) {
            console.error(`[${title}]`, message, details);
        }
    }

    /**
     * Show success notification
     * @param {string} title - Success title
     * @param {string} message - Success message
     */
    success(title, message) {
        this.toast(`✅ ${title}: ${message}`, 'success', 3000);
    }
}

// Global instance
const Notify = new NotificationSystem();

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .modal.show {
        display: block;
    }

    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 9998;
    }
`;
document.head.appendChild(style);

// Export for use
window.Notify = Notify;
