/**
 * PWA Client Manager - Gestion offline et sync côté client
 * Inclut: Service Worker registration, offline detection, sync queue management
 */

class PWAManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.swRegistration = null;
    this.messageChannel = null;
    this.offlineQueue = [];
    this.syncInProgress = false;
    
    // Événements
    this.onOnline = null;
    this.onOffline = null;
    this.onSyncStart = null;
    this.onSyncComplete = null;
    this.onSyncError = null;
  }

  /**
   * Initialiser le PWA Manager
   */
  async init() {
    console.log('PWA Manager: Initialisation');
    
    // Enregistrer le Service Worker
    if ('serviceWorker' in navigator) {
      try {
        this.swRegistration = await navigator.serviceWorker.register(
          '/static/js/service_worker_advanced.js',
          { scope: '/' }
        );
        console.log('Service Worker enregistré:', this.swRegistration);
        
        // Écouter les mises à jour
        this.swRegistration.addEventListener('updatefound', () => {
          const newWorker = this.swRegistration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });
      } catch (error) {
        console.error('Erreur enregistrement Service Worker:', error);
      }
    }
    
    // Écouter les changements online/offline
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
    
    // Écouter les messages du Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        this.handleServiceWorkerMessage(event.data);
      });
    }
    
    console.log('PWA Manager: Initialisé');
  }

  /**
   * Envoyer un message au Service Worker
   */
  postToServiceWorker(message) {
    if (navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage(message);
    }
  }

  /**
   * Traiter les messages du Service Worker
   */
  handleServiceWorkerMessage(message) {
    console.log('Message du Service Worker:', message);
    
    switch (message.type) {
      case 'SYNC_COMPLETE':
        this.handleSyncComplete(message);
        break;
      case 'UPDATE_AVAILABLE':
        this.showUpdateNotification();
        break;
    }
  }

  /**
   * Obtenir le statut online
   */
  getOnlineStatus() {
    return this.isOnline;
  }

  /**
   * Gérer le retour online
   */
  async handleOnline() {
    console.log('PWA: Retour online');
    this.isOnline = true;
    
    if (this.onOnline) {
      this.onOnline();
    }
    
    // Montrer notification
    this.showNotification('Reconnecté', 'Synchronisation des données...');
    
    // Déclencher la synchronisation
    await this.syncNow();
  }

  /**
   * Gérer le passage offline
   */
  handleOffline() {
    console.log('PWA: Passage offline');
    this.isOnline = false;
    
    if (this.onOffline) {
      this.onOffline();
    }
    
    // Montrer notification
    this.showNotification('Mode offline', 'Les changements seront synchronisés à la reconnexion');
  }

  /**
   * Mettre en queue une action offline
   */
  async queueAction(request) {
    console.log('Mise en queue:', request.url);
    
    const action = {
      id: this.generateId(),
      url: request.url,
      method: request.method,
      body: request.body,
      timestamp: Date.now()
    };
    
    this.offlineQueue.push(action);
    
    // Sauvegarder en localStorage
    this.saveOfflineQueue();
    
    // Notifier le Service Worker
    if (navigator.serviceWorker.controller) {
      this.postToServiceWorker({
        type: 'QUEUE_ACTION',
        data: { request }
      });
    }
    
    return action;
  }

  /**
   * Synchroniser maintenant
   */
  async syncNow() {
    if (this.syncInProgress || !this.isOnline) {
      console.log('Sync already in progress or offline');
      return;
    }
    
    this.syncInProgress = true;
    
    if (this.onSyncStart) {
      this.onSyncStart();
    }
    
    try {
      console.log('Démarrage de la synchronisation');
      
      // Synchroniser la queue locale
      await this.syncLocalQueue();
      
      // Demander au Service Worker de synchroniser
      this.postToServiceWorker({
        type: 'SYNC_NOW'
      });
      
      // Attendre la réponse
      await this.waitForSyncResponse();
      
      if (this.onSyncComplete) {
        this.onSyncComplete({
          status: 'success',
          message: 'Synchronisation complète'
        });
      }
      
      this.showNotification('Synchronisé', 'Vos données sont à jour');
      
    } catch (error) {
      console.error('Erreur synchronisation:', error);
      
      if (this.onSyncError) {
        this.onSyncError(error);
      }
      
      this.showNotification('Erreur sync', 'Veuillez réessayer');
    } finally {
      this.syncInProgress = false;
    }
  }

  /**
   * Synchroniser la queue locale
   */
  async syncLocalQueue() {
    const queue = this.getOfflineQueue();
    
    for (const action of queue) {
      try {
        const response = await fetch(action.url, {
          method: action.method,
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: action.body
        });
        
        if (response.ok) {
          this.removeFromQueue(action.id);
        }
      } catch (error) {
        console.error('Erreur sync action:', error);
      }
    }
  }

  /**
   * Attendre la réponse de sync
   */
  waitForSyncResponse() {
    return new Promise((resolve) => {
      const timeout = setTimeout(resolve, 5000);
      
      if (navigator.serviceWorker.controller) {
        const listener = (event) => {
          if (event.data.type === 'SYNC_COMPLETE') {
            clearTimeout(timeout);
            navigator.serviceWorker.removeEventListener('message', listener);
            resolve();
          }
        };
        
        navigator.serviceWorker.addEventListener('message', listener);
      } else {
        clearTimeout(timeout);
        resolve();
      }
    });
  }

  /**
   * Traiter la synchronisation complète
   */
  handleSyncComplete(message) {
    console.log('Sync complète:', message);
    
    if (this.onSyncComplete) {
      this.onSyncComplete({
        status: message.status,
        message: message.message
      });
    }
  }

  /**
   * Obtenir la queue offline du localStorage
   */
  getOfflineQueue() {
    const queue = localStorage.getItem('offlineQueue');
    return queue ? JSON.parse(queue) : [];
  }

  /**
   * Sauvegarder la queue offline
   */
  saveOfflineQueue() {
    localStorage.setItem('offlineQueue', JSON.stringify(this.offlineQueue));
  }

  /**
   * Supprimer de la queue
   */
  removeFromQueue(id) {
    this.offlineQueue = this.offlineQueue.filter(item => item.id !== id);
    this.saveOfflineQueue();
  }

  /**
   * Vider la queue
   */
  clearQueue() {
    this.offlineQueue = [];
    this.saveOfflineQueue();
  }

  /**
   * Obtenir la taille du cache
   */
  async getCacheSize() {
    return new Promise((resolve) => {
      const listener = (event) => {
        if (event.data.cacheSize !== undefined) {
          navigator.serviceWorker.removeEventListener('message', listener);
          resolve(event.data.cacheSize);
        }
      };
      
      navigator.serviceWorker.addEventListener('message', listener);
      this.postToServiceWorker({ type: 'GET_CACHE_SIZE' });
      
      // Timeout après 5 secondes
      setTimeout(() => resolve(0), 5000);
    });
  }

  /**
   * Nettoyer le cache
   */
  async clearCache() {
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(name => caches.delete(name))
      );
      console.log('Cache nettoyé');
      return true;
    }
    return false;
  }

  /**
   * Montrer une notification
   */
  showNotification(title, message) {
    if (!('Notification' in window)) {
      return;
    }
    
    if (Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: '/static/img/icon-192x192.png'
      });
    } else if (Notification.permission !== 'denied') {
      Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
          new Notification(title, {
            body: message,
            icon: '/static/img/icon-192x192.png'
          });
        }
      });
    }
  }

  /**
   * Montrer notification de mise à jour
   */
  showUpdateNotification() {
    const message = document.createElement('div');
    message.className = 'pwa-update-notification';
    message.innerHTML = `
      <div class="pwa-update-content">
        <p>Une nouvelle version est disponible</p>
        <button id="pwa-update-btn" class="btn btn-sm btn-primary">Mettre à jour</button>
        <button id="pwa-update-close" class="btn btn-sm btn-secondary">Plus tard</button>
      </div>
    `;
    
    document.body.appendChild(message);
    
    document.getElementById('pwa-update-btn').addEventListener('click', () => {
      this.updateServiceWorker();
    });
    
    document.getElementById('pwa-update-close').addEventListener('click', () => {
      message.remove();
    });
  }

  /**
   * Mettre à jour le Service Worker
   */
  updateServiceWorker() {
    if (navigator.serviceWorker.controller) {
      this.postToServiceWorker({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  }

  /**
   * Demander la permission de notifications
   */
  async requestNotificationPermission() {
    if (!('Notification' in window)) {
      console.log('Notifications non supportées');
      return false;
    }
    
    if (Notification.permission === 'granted') {
      return true;
    }
    
    if (Notification.permission !== 'denied') {
      const permission = await Notification.requestPermission();
      return permission === 'granted';
    }
    
    return false;
  }

  /**
   * Souscrire aux notifications push
   */
  async subscribeToPush(publicKey) {
    if (!this.swRegistration || !('pushManager' in this.swRegistration)) {
      console.log('Push Manager non disponible');
      return null;
    }
    
    try {
      const subscription = await this.swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(publicKey)
      });
      
      console.log('Push subscription:', subscription);
      return subscription;
    } catch (error) {
      console.error('Erreur push subscription:', error);
      return null;
    }
  }

  /**
   * Convertir URL base64 en Uint8Array (pour les clés push)
   */
  urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');
    
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    
    return outputArray;
  }

  /**
   * Générer un ID unique
   */
  generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Obtenir les infos du Service Worker
   */
  getServiceWorkerInfo() {
    return {
      isRegistered: !!this.swRegistration,
      isActive: !!navigator.serviceWorker.controller,
      state: navigator.serviceWorker.controller?.state || 'uncontrolled',
      isOnline: this.isOnline,
      queueSize: this.offlineQueue.length
    };
  }
}

// Instance globale
window.pwaManager = null;

/**
 * Initialiser le PWA Manager au chargement du document
 */
document.addEventListener('DOMContentLoaded', async () => {
  if (!window.pwaManager) {
    window.pwaManager = new PWAManager();
    await window.pwaManager.init();
    
    // Callbacks pour l'UI
    window.pwaManager.onOnline = () => {
      // Mettre à jour l'UI
      document.body.classList.remove('offline');
      document.body.classList.add('online');
    };
    
    window.pwaManager.onOffline = () => {
      // Mettre à jour l'UI
      document.body.classList.remove('online');
      document.body.classList.add('offline');
    };
  }
});

