/**
 * Service Worker Avancé - PWA Offline Complet
 * Inclut: Background Sync, Offline Queue, Cache Versioning, Conflict Resolution
 * 
 * Features:
 * - Cache versioning et update notifications
 * - Background sync pour les actions offline
 * - Offline queue management
 * - Push notifications
 * - Intelligent caching strategies
 */

const CACHE_VERSION = 'v1';
const CACHE_KEYS = {
  STATIC: `bnc-static-${CACHE_VERSION}`,
  DYNAMIC: `bnc-dynamic-${CACHE_VERSION}`,
  IMAGES: `bnc-images-${CACHE_VERSION}`,
  API: `bnc-api-${CACHE_VERSION}`,
};

const OFFLINE_URL = '/offline/';
const API_ENDPOINT = '/api/';

// URLs à mettre en cache au service worker installation
const URLS_TO_CACHE = [
  '/',
  '/offline/',
  '/static/css/bootstrap.min.css',
  '/static/css/main.css',
  '/static/js/jquery.min.js',
  '/static/js/bootstrap.min.js',
  '/manifest.json',
];

// ============================================================================
// INSTALLATION - Mettre en cache les assets statiques
// ============================================================================

self.addEventListener('install', (event) => {
  console.log('Service Worker: Installation en cours...');
  
  event.waitUntil(
    caches.open(CACHE_KEYS.STATIC)
      .then((cache) => {
        console.log('Service Worker: Mise en cache des assets statiques');
        return cache.addAll(URLS_TO_CACHE);
      })
      .then(() => {
        console.log('Service Worker: Installation complète');
        // Force le nouveau service worker à prendre le contrôle
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Erreur installation', error);
      })
  );
});

// ============================================================================
// ACTIVATION - Nettoyer les vieilles caches
// ============================================================================

self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activation en cours...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // Supprimer les caches avec des versions anciennes
            if (!Object.values(CACHE_KEYS).includes(cacheName)) {
              console.log(`Service Worker: Suppression de l'ancienne cache: ${cacheName}`);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complète');
        return self.clients.claim();
      })
      .catch((error) => {
        console.error('Service Worker: Erreur activation', error);
      })
  );
});

// ============================================================================
// FETCH - Stratégie de caching intelligente
// ============================================================================

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Ignorer les requêtes non-HTTP(S)
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // Stratégie 1: API Requests - Cache, falling back to network
  if (url.pathname.startsWith(API_ENDPOINT)) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Mettre en cache les réponses réussies
          if (response.status === 200) {
            const cacheClone = response.clone();
            caches.open(CACHE_KEYS.API).then((cache) => {
              cache.put(request, cacheClone);
            });
          }
          return response;
        })
        .catch(() => {
          // En offline, retourner la version en cache
          return caches.match(request)
            .then((cachedResponse) => {
              if (cachedResponse) {
                return cachedResponse;
              }
              // Si pas en cache, retourner une réponse offline
              return createOfflineResponse('API not available offline');
            });
        })
    );
  }
  
  // Stratégie 2: HTML Pages - Cache, falling back to offline page
  else if (request.method === 'GET' && request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Mettre à jour le cache pour les pages HTML
          if (response.status === 200) {
            const cacheClone = response.clone();
            caches.open(CACHE_KEYS.DYNAMIC).then((cache) => {
              cache.put(request, cacheClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Retourner la page en cache ou la page offline
          return caches.match(request)
            .then((cachedResponse) => {
              return cachedResponse || caches.match(OFFLINE_URL);
            });
        })
    );
  }
  
  // Stratégie 3: Images - Cache first
  else if (request.method === 'GET' && request.destination === 'image') {
    event.respondWith(
      caches.open(CACHE_KEYS.IMAGES)
        .then((cache) => {
          return cache.match(request)
            .then((cachedResponse) => {
              if (cachedResponse) {
                return cachedResponse;
              }
              
              // Fetcher et mettre en cache
              return fetch(request)
                .then((response) => {
                  if (response.status === 200) {
                    const cacheClone = response.clone();
                    cache.put(request, cacheClone);
                  }
                  return response;
                })
                .catch(() => {
                  // Image par défaut si offline
                  return createOfflineImage();
                });
            });
        })
    );
  }
  
  // Stratégie 4: Static assets - Network first
  else if (request.method === 'GET') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Mettre à jour la cache avec la nouvelle version
          if (response.status === 200) {
            const cacheClone = response.clone();
            caches.open(CACHE_KEYS.STATIC).then((cache) => {
              cache.put(request, cacheClone);
            });
          }
          return response;
        })
        .catch(() => {
          // Utiliser la version en cache
          return caches.match(request);
        })
    );
  }
  
  // Stratégie 5: POST requests - Sync queue si offline
  else if (request.method === 'POST' || request.method === 'PUT' || request.method === 'DELETE') {
    event.respondWith(
      fetch(request)
        .then((response) => response)
        .catch((error) => {
          // En offline, mettre l'action en queue
          queueAction(request);
          return createQueuedResponse();
        })
    );
  }
});

// ============================================================================
// BACKGROUND SYNC - Synchroniser les actions offline
// ============================================================================

self.addEventListener('sync', (event) => {
  console.log('Background Sync: Démarrage de la synchronisation');
  
  if (event.tag === 'sync-offline-queue') {
    event.waitUntil(
      syncOfflineQueue()
        .then(() => {
          console.log('Background Sync: Synchronisation réussie');
          // Notifier le client
          self.clients.matchAll().then((clients) => {
            clients.forEach((client) => {
              client.postMessage({
                type: 'SYNC_COMPLETE',
                status: 'success',
                message: 'Synchronisation complète'
              });
            });
          });
        })
        .catch((error) => {
          console.error('Background Sync: Erreur', error);
          // Rejeu plus tard
          throw error;
        })
    );
  }
});

// ============================================================================
// PUSH NOTIFICATIONS
// ============================================================================

self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body || 'Nouvelle notification',
      icon: '/static/img/icon-192x192.png',
      badge: '/static/img/badge-72x72.png',
      tag: data.tag || 'notification',
      requireInteraction: data.requireInteraction || false,
      data: data.data || {}
    };
    
    event.waitUntil(
      self.registration.showNotification(data.title || 'BNC', options)
    );
  }
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  // Ouvrir ou focus la fenêtre
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then((clientList) => {
      // Chercher si une fenêtre existe déjà
      for (let client of clientList) {
        if (client.url === event.notification.data.url && 'focus' in client) {
          return client.focus();
        }
      }
      // Ouvrir une nouvelle fenêtre
      if (self.clients.openWindow) {
        return self.clients.openWindow(event.notification.data.url || '/');
      }
    })
  );
});

// ============================================================================
// MESSAGE HANDLING - Communication avec le client
// ============================================================================

self.addEventListener('message', (event) => {
  const { type, data } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      // Mettre à jour le service worker immédiatement
      self.skipWaiting();
      break;
    
    case 'QUEUE_ACTION':
      // Mettre en queue une action offline
      queueAction(data.request);
      event.ports[0].postMessage({
        status: 'queued',
        message: 'Action mise en queue pour sync'
      });
      break;
    
    case 'SYNC_NOW':
      // Déclencher la synchronisation manuellement
      syncOfflineQueue().then(() => {
        event.ports[0].postMessage({
          status: 'synced',
          message: 'Synchronisation complète'
        });
      });
      break;
    
    case 'GET_CACHE_SIZE':
      // Obtenir la taille du cache
      getCacheSize().then((size) => {
        event.ports[0].postMessage({
          cacheSize: size
        });
      });
      break;
  }
});

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Mettre une action en queue pour sync offline
 */
async function queueAction(request) {
  try {
    const db = await openIndexedDB();
    const tx = db.transaction('offlineQueue', 'readwrite');
    const store = tx.objectStore('offlineQueue');
    
    const action = {
      id: generateId(),
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers),
      body: await request.clone().text(),
      timestamp: Date.now(),
      attempts: 0
    };
    
    await store.add(action);
    console.log('Action mise en queue:', action);
    
    // Déclencher une sync
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      await self.registration.sync.register('sync-offline-queue');
    }
  } catch (error) {
    console.error('Erreur mise en queue:', error);
  }
}

/**
 * Synchroniser la queue offline
 */
async function syncOfflineQueue() {
  try {
    const db = await openIndexedDB();
    const tx = db.transaction('offlineQueue', 'readonly');
    const store = tx.objectStore('offlineQueue');
    const actions = await store.getAll();
    
    let syncedCount = 0;
    let failedCount = 0;
    
    for (const action of actions) {
      try {
        const request = new Request(action.url, {
          method: action.method,
          headers: action.headers,
          body: action.body
        });
        
        const response = await fetch(request);
        
        if (response.ok) {
          // Supprimer de la queue
          const deleteTx = db.transaction('offlineQueue', 'readwrite');
          await deleteTx.objectStore('offlineQueue').delete(action.id);
          syncedCount++;
        } else {
          failedCount++;
          action.attempts++;
          
          // Remettre à jour avec le nombre de tentatives
          const updateTx = db.transaction('offlineQueue', 'readwrite');
          await updateTx.objectStore('offlineQueue').put(action);
        }
      } catch (error) {
        console.error('Erreur sync action:', error);
        failedCount++;
        action.attempts++;
      }
    }
    
    console.log(`Sync complete: ${syncedCount} réussis, ${failedCount} échoués`);
    
    return { syncedCount, failedCount };
  } catch (error) {
    console.error('Erreur sync queue:', error);
    throw error;
  }
}

/**
 * Ouvrir ou créer la IndexedDB
 */
async function openIndexedDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('BNC', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('offlineQueue')) {
        db.createObjectStore('offlineQueue', { keyPath: 'id' });
      }
    };
  });
}

/**
 * Générer un ID unique
 */
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Obtenir la taille du cache
 */
async function getCacheSize() {
  let size = 0;
  for (const key of Object.values(CACHE_KEYS)) {
    const cache = await caches.open(key);
    const requests = await cache.keys();
    
    for (const request of requests) {
      const response = await cache.match(request);
      if (response) {
        const blob = await response.blob();
        size += blob.size;
      }
    }
  }
  return size;
}

/**
 * Créer une réponse offline
 */
function createOfflineResponse(message = 'You are offline') {
  return new Response(
    JSON.stringify({
      offline: true,
      message: message
    }),
    {
      status: 503,
      statusText: 'Service Unavailable',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
}

/**
 * Créer une réponse "action en queue"
 */
function createQueuedResponse() {
  return new Response(
    JSON.stringify({
      queued: true,
      message: 'Action mise en queue pour synchronisation ultérieure',
      syncWhenOnline: true
    }),
    {
      status: 202,
      statusText: 'Accepted',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  );
}

/**
 * Créer une image offline
 */
function createOfflineImage() {
  const svg = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="#ddd" width="100" height="100"/><text x="50" y="50" text-anchor="middle" dy=".3em" fill="#999">Offline</text></svg>';
  return new Response(svg, {
    headers: {
      'Content-Type': 'image/svg+xml'
    }
  });
}

console.log('Service Worker: Chargé et prêt');

