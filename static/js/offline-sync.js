/**
 * Offline Sync Manager
 * Handles background synchronization of offline actions
 */

class OfflineSyncManager {
    constructor() {
        this.pendingActions = [];
        this.isOnline = navigator.onLine;
        this.syncInProgress = false;
        this.maxRetries = 3;
        this.init();
    }

    init() {
        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // Listen for Service Worker messages
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', (event) => {
                this.handleServiceWorkerMessage(event);
            });
        }

        console.log('[OfflineSync] Manager initialized');
    }

    /**
     * Handle coming online
     */
    handleOnline() {
        console.log('[OfflineSync] Connection restored');
        this.isOnline = true;
        this.syncPendingActions();
    }

    /**
     * Handle going offline
     */
    handleOffline() {
        console.log('[OfflineSync] Connection lost');
        this.isOnline = false;
    }

    /**
     * Handle messages from Service Worker
     */
    handleServiceWorkerMessage(event) {
        const { type, action } = event.data;

        if (type === 'SYNC_COMPLETE') {
            console.log('[OfflineSync] Sync completed for:', action);
            this.showSyncNotification(action);
        }
    }

    /**
     * Save rating for offline sync
     */
    async saveRatingOffline(bookId, rating, review = '') {
        try {
            const manager = window.offlineDataManager;
            if (manager) {
                await manager.saveRating(bookId, rating, review);
                this.pendingActions.push({
                    type: 'rating',
                    bookId,
                    data: { rating, review },
                    timestamp: Date.now(),
                    retries: 0,
                });

                console.log('[OfflineSync] Rating saved offline:', bookId);
                return true;
            }
        } catch (error) {
            console.error('[OfflineSync] Error saving rating:', error);
            return false;
        }
    }

    /**
     * Save reading progress for offline sync
     */
    async saveProgressOffline(bookId, progress) {
        try {
            const manager = window.offlineDataManager;
            if (manager) {
                await manager.saveReadingProgress(bookId, progress);
                this.pendingActions.push({
                    type: 'progress',
                    bookId,
                    data: { progress },
                    timestamp: Date.now(),
                    retries: 0,
                });

                console.log('[OfflineSync] Progress saved offline:', bookId);
                return true;
            }
        } catch (error) {
            console.error('[OfflineSync] Error saving progress:', error);
            return false;
        }
    }

    /**
     * Sync all pending actions
     */
    async syncPendingActions() {
        if (this.syncInProgress || this.pendingActions.length === 0) {
            return;
        }

        this.syncInProgress = true;
        console.log('[OfflineSync] Starting sync of', this.pendingActions.length, 'actions');

        const actionsToSync = [...this.pendingActions];
        this.pendingActions = [];

        for (const action of actionsToSync) {
            const success = await this.syncAction(action);

            if (!success) {
                action.retries++;
                if (action.retries < this.maxRetries) {
                    this.pendingActions.push(action);
                } else {
                    console.error('[OfflineSync] Max retries reached for:', action);
                }
            }
        }

        this.syncInProgress = false;

        if (this.pendingActions.length === 0) {
            console.log('[OfflineSync] All actions synced successfully');
            this.showSyncNotification('All changes synced');
        }
    }

    /**
     * Sync single action
     */
    async syncAction(action) {
        try {
            switch (action.type) {
                case 'rating':
                    return await this.syncRating(action);
                case 'progress':
                    return await this.syncProgress(action);
                default:
                    console.warn('[OfflineSync] Unknown action type:', action.type);
                    return false;
            }
        } catch (error) {
            console.error('[OfflineSync] Error syncing action:', error);
            return false;
        }
    }

    /**
     * Sync rating
     */
    async syncRating(action) {
        try {
            const { bookId, data } = action;

            const response = await fetch(`/api/books/${bookId}/ratings/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                // Mark as synced in IndexedDB
                // This is handled by the Service Worker background sync
                console.log('[OfflineSync] Rating synced for book:', bookId);
                return true;
            } else {
                console.error('[OfflineSync] Failed to sync rating:', response.status);
                return false;
            }
        } catch (error) {
            console.error('[OfflineSync] Error syncing rating:', error);
            return false;
        }
    }

    /**
     * Sync reading progress
     */
    async syncProgress(action) {
        try {
            const { bookId, data } = action;

            const response = await fetch(`/api/books/${bookId}/progress/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(data),
            });

            if (response.ok) {
                console.log('[OfflineSync] Progress synced for book:', bookId);
                return true;
            } else {
                console.error('[OfflineSync] Failed to sync progress:', response.status);
                return false;
            }
        } catch (error) {
            console.error('[OfflineSync] Error syncing progress:', error);
            return false;
        }
    }

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        return (
            document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
            document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1] ||
            ''
        );
    }

    /**
     * Show sync notification
     */
    showSyncNotification(message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            navigator.serviceWorker.ready.then((registration) => {
                registration.showNotification('BNC Sync', {
                    body: message,
                    icon: '/static/images/icon-192x192.png',
                    badge: '/static/images/icon-192x192.png',
                    tag: 'sync-notification',
                });
            });
        }
    }

    /**
     * Get pending actions count
     */
    getPendingCount() {
        return this.pendingActions.length;
    }

    /**
     * Get pending actions
     */
    getPendingActions() {
        return this.pendingActions;
    }
}

// Initialize
window.OfflineSyncManager = OfflineSyncManager;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.offlineSyncManager = new OfflineSyncManager();
    });
} else {
    window.offlineSyncManager = new OfflineSyncManager();
}
