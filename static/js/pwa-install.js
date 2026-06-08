/**
 * PWA Installation Manager
 * Handles PWA installation prompts and installation management
 */

class PWAInstallManager {
    constructor() {
        this.deferredPrompt = null;
        this.isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        this.installPromptShown = false;
        this.init();
    }

    init() {
        // Capture beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            this.handleBeforeInstallPrompt(e);
        });

        // Listen for successful installation
        window.addEventListener('appinstalled', () => {
            this.handleAppInstalled();
        });

        // Check if app is already installed
        this.checkIfInstalled();

        // Fallback helper:
        // iOS does not fire beforeinstallprompt, and some Android browsers
        // hide it until engagement criteria are met.
        setTimeout(() => {
            if (!this.deferredPrompt && !this.isRunningStandalone()) {
                this.showManualInstallHelp();
            }
        }, 2500);
    }

    /**
     * Handle beforeinstallprompt event (Android)
     */
    handleBeforeInstallPrompt(e) {
        console.log('[PWA] beforeinstallprompt fired');
        e.preventDefault();
        this.deferredPrompt = e;

        // Show install button
        this.showInstallPrompt();
    }

    /**
     * Show install prompt to user
     */
    showInstallPrompt() {
        const installButton = document.getElementById('pwa-install-button');
        const installCard = document.getElementById('pwa-install-card');

        if (installButton && installCard && !this.installPromptShown) {
            this.installPromptShown = true;
            installCard.style.display = 'block';

            installButton.addEventListener('click', () => {
                this.promptInstall();
            }, { once: true });
        }
    }

    /**
     * Prompt user to install app
     */
    async promptInstall() {
        if (!this.deferredPrompt) {
            return;
        }

        this.deferredPrompt.prompt();
        const { outcome } = await this.deferredPrompt.userChoice;

        console.log(`[PWA] Installation ${outcome}`);

        if (outcome === 'accepted') {
            this.deferredPrompt = null;
            this.hideInstallPrompt();
        }
    }

    /**
     * Handle successful app installation
     */
    handleAppInstalled() {
        console.log('[PWA] App successfully installed!');
        this.hideInstallPrompt();
        this.showSuccessMessage('App installed with success! You can now use it offline.');
    }

    /**
     * Hide install prompt
     */
    hideInstallPrompt() {
        const installCard = document.getElementById('pwa-install-card');
        if (installCard) {
            installCard.style.display = 'none';
        }
    }

    /**
     * Check if app is already installed
     */
    checkIfInstalled() {
        if (window.navigator.standalone === true) {
            console.log('[PWA] App is running in standalone mode');
            document.documentElement.classList.add('pwa-standalone');
        } else if (window.matchMedia('(display-mode: standalone)').matches) {
            console.log('[PWA] App is running as PWA');
            document.documentElement.classList.add('pwa-installed');
        }
    }

    isRunningStandalone() {
        return window.navigator.standalone === true || window.matchMedia('(display-mode: standalone)').matches;
    }

    showManualInstallHelp() {
        const installButton = document.getElementById('pwa-install-button');
        const installCard = document.getElementById('pwa-install-card');
        const helperText = installCard?.querySelector('.text-secondary');
        if (!installButton || !installCard) return;
        if (this.isRunningStandalone()) return;

        installCard.style.display = 'block';

        if (this.isIOS) {
            if (helperText) {
                helperText.textContent = "Sur iPhone: touchez Partager puis 'Sur l'écran d'accueil'.";
            }
            installButton.innerHTML = '<i class="fas fa-mobile-alt me-2"></i>Guide iPhone';
            installButton.onclick = () => {
                alert("iPhone: 1) Ouvrez le menu Partager 2) Choisissez 'Sur l\\'écran d\\'accueil' 3) Validez Ajouter.");
            };
            return;
        }

        if (helperText) {
            helperText.textContent = "Si le bouton d'installation n'apparaît pas, utilisez le menu du navigateur puis 'Installer l'application'.";
        }
        installButton.innerHTML = '<i class="fas fa-download me-2"></i>Guide d’installation';
        installButton.onclick = () => {
            alert("Android: ouvrez le menu du navigateur puis 'Installer l\\'application' / 'Ajouter à l\\'écran d\\'accueil'.");
        };
    }

    /**
     * Show success message
     */
    showSuccessMessage(message) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show fixed-bottom';
        alert.role = 'alert';
        alert.style.margin = '1rem';
        alert.style.zIndex = '9999';
        alert.innerHTML = `
            <i class="fas fa-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);

        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

/**
 * Register Service Worker
 */
async function registerServiceWorker() {
    if (!('serviceWorker' in navigator)) {
        console.log('[PWA] Service Workers not supported');
        return;
    }

    try {
        // Always register from root so scope and script stay consistent.
        const registration = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
        console.log('[PWA] Service Worker registered:', registration);

        // Check for updates periodically
        setInterval(() => {
            registration.update();
        }, 60000); // Check every minute

        // Listen for controller change (new version available)
        navigator.serviceWorker.addEventListener('controllerchange', () => {
            console.log('[PWA] New Service Worker version available');
            showUpdatePrompt();
        });

        return registration;
    } catch (error) {
        console.error('[PWA] Service Worker registration failed:', error);
    }
}

/**
 * Handle offline/online status
 */
function setupConnectivityHandling() {
    const updateOnlineStatus = () => {
        if (navigator.onLine) {
            console.log('[PWA] Back online');
            document.documentElement.classList.remove('is-offline');
            document.documentElement.classList.add('is-online');

            // Trigger sync
            if ('serviceWorker' in navigator && 'SyncManager' in window) {
                navigator.serviceWorker.ready.then((registration) => {
                    registration.sync.register('sync-all').catch((err) => {
                        console.warn('[PWA] Sync registration failed:', err);
                    });
                });
            }

            // Show notification
            showNotification('Back Online', {
                body: 'Connection restored. Syncing your data...',
                icon: '/static/images/icon-192x192.png',
            });
        } else {
            console.log('[PWA] You are offline');
            document.documentElement.classList.remove('is-online');
            document.documentElement.classList.add('is-offline');

            // Show notification
            showNotification('You are Offline', {
                body: 'You can still read downloaded books and use cached features.',
                icon: '/static/images/icon-192x192.png',
            });
        }
    };

    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);

    // Check initial status
    updateOnlineStatus();
}

/**
 * Show notification
 */
function showNotification(title, options = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
        navigator.serviceWorker.ready.then((registration) => {
            registration.showNotification(title, {
                icon: '/static/images/icon-192x192.png',
                badge: '/static/images/icon-192x192.png',
                ...options,
            });
        });
    }
}

/**
 * Request notification permission
 */
async function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('[PWA] Notifications not supported');
        return false;
    }

    if (Notification.permission === 'granted') {
        return true;
    }

    if (Notification.permission !== 'denied') {
        try {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        } catch (error) {
            console.error('[PWA] Notification permission error:', error);
            return false;
        }
    }

    return false;
}

/**
 * Show update prompt
 */
function showUpdatePrompt() {
    const alert = document.createElement('div');
    alert.className = 'alert alert-info alert-dismissible fade show fixed-bottom';
    alert.role = 'alert';
    alert.style.margin = '1rem';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="fas fa-sync"></i> 
        <strong>Update Available!</strong> A new version of BNC is available.
        <button class="btn btn-sm btn-primary ms-2" onclick="location.reload()">
            Update Now
        </button>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
}

/**
 * IndexedDB Management
 */
class OfflineDataManager {
    constructor() {
        this.db = null;
        this.initDB();
    }

    /**
     * Initialize IndexedDB
     */
    async initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open('bnc-offline', 1);

            request.onerror = () => {
                console.error('[IndexedDB] Error opening database');
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('[IndexedDB] Database opened successfully');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object stores
                if (!db.objectStoreNames.contains('books')) {
                    const bookStore = db.createObjectStore('books', { keyPath: 'id' });
                    bookStore.createIndex('date', 'date', { unique: false });
                }

                if (!db.objectStoreNames.contains('readings')) {
                    const readingStore = db.createObjectStore('readings', { keyPath: 'id', autoIncrement: true });
                    readingStore.createIndex('bookId', 'bookId', { unique: false });
                    readingStore.createIndex('timestamp', 'timestamp', { unique: false });
                }

                if (!db.objectStoreNames.contains('ratings')) {
                    const ratingStore = db.createObjectStore('ratings', { keyPath: 'id', autoIncrement: true });
                    ratingStore.createIndex('bookId', 'bookId', { unique: false });
                    ratingStore.createIndex('synced', 'synced', { unique: false });
                }

                if (!db.objectStoreNames.contains('downloads')) {
                    const downloadStore = db.createObjectStore('downloads', { keyPath: 'id', autoIncrement: true });
                    downloadStore.createIndex('bookId', 'bookId', { unique: false });
                    downloadStore.createIndex('status', 'status', { unique: false });
                }

                console.log('[IndexedDB] Object stores created');
            };
        });
    }

    /**
     * Save book data for offline access
     */
    async saveBook(bookData) {
        const tx = this.db.transaction('books', 'readwrite');
        const store = tx.objectStore('books');
        const data = {
            ...bookData,
            date: new Date().toISOString(),
        };
        store.put(data);

        return new Promise((resolve, reject) => {
            tx.oncomplete = () => {
                console.log('[IndexedDB] Book saved:', bookData.id);
                resolve();
            };
            tx.onerror = () => reject(tx.error);
        });
    }

    /**
     * Save reading progress
     */
    async saveReadingProgress(bookId, progress) {
        const tx = this.db.transaction('readings', 'readwrite');
        const store = tx.objectStore('readings');
        const data = {
            bookId,
            progress,
            timestamp: new Date().toISOString(),
            synced: false,
        };
        store.add(data);

        return new Promise((resolve, reject) => {
            tx.oncomplete = () => {
                console.log('[IndexedDB] Reading progress saved:', bookId);
                resolve();
            };
            tx.onerror = () => reject(tx.error);
        });
    }

    /**
     * Save rating
     */
    async saveRating(bookId, rating, review) {
        const tx = this.db.transaction('ratings', 'readwrite');
        const store = tx.objectStore('ratings');
        const data = {
            bookId,
            rating,
            review,
            timestamp: new Date().toISOString(),
            synced: false,
        };
        store.add(data);

        return new Promise((resolve, reject) => {
            tx.oncomplete = () => {
                console.log('[IndexedDB] Rating saved:', bookId);
                resolve();
            };
            tx.onerror = () => reject(tx.error);
        });
    }

    /**
     * Get all unsynced ratings
     */
    async getUnsyncedRatings() {
        const tx = this.db.transaction('ratings', 'readonly');
        const store = tx.objectStore('ratings');
        const index = store.index('synced');
        const range = IDBKeyRange.only(false);
        const request = index.getAll(range);

        return new Promise((resolve, reject) => {
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Mark rating as synced
     */
    async markRatingAsSynced(ratingId) {
        const tx = this.db.transaction('ratings', 'readwrite');
        const store = tx.objectStore('ratings');
        const request = store.get(ratingId);

        request.onsuccess = () => {
            const rating = request.result;
            rating.synced = true;
            store.put(rating);
        };

        return new Promise((resolve, reject) => {
            tx.oncomplete = () => resolve();
            tx.onerror = () => reject(tx.error);
        });
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        init();
    });
} else {
    init();
}

async function init() {
    // Register Service Worker
    await registerServiceWorker();

    // Setup connectivity handling
    setupConnectivityHandling();

    // Initialize PWA install manager
    new PWAInstallManager();

    // Initialize offline data manager
    window.offlineDataManager = new OfflineDataManager();

    // Request notification permission
    await requestNotificationPermission();

    console.log('[PWA] Initialization complete');
}

// Export for use in other scripts
window.PWAInstallManager = PWAInstallManager;
window.OfflineDataManager = OfflineDataManager;
window.showNotification = showNotification;
window.registerServiceWorker = registerServiceWorker;
