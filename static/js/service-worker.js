/*
SERVICE WORKER - MODE HORS-LIGNE COMPLET (PWA)
Version 2.0 - Décembre 2025
Stratégies: cache-first (assets), network-first (API), PDF pour offline
IndexedDB pour sync background et données locales
*/

const CACHE_NAME = 'calures-v5';
const API_CACHE = 'calures-api-v5';
const PDF_CACHE = 'calures-pdf-v5';
const RUNTIME_CACHE = 'calures-runtime-v5';

// Assets statiques à pré-cacher
const STATIC_ASSETS = [
    '/',
    '/fr/',
    '/fr/books/',
    '/offline/',
    '/pwa/manifest.json',
    '/sw.js',
    '/static/css/global.css',
    '/static/js/pwa-install.js',
    '/static/js/pdf.min.js',
    '/static/js/pdf.worker.min.js',
    '/static/images/icon-192x192.png',
    '/static/images/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// ============================================================================
// INSTALLATION - Pré-cacher les assets essentiels
// ============================================================================
self.addEventListener('install', event => {
    console.log('[SW] Installation démarrée v2.1');
    
    event.waitUntil(
        (async () => {
            try {
                const cache = await caches.open(CACHE_NAME);
                await Promise.allSettled(
                    STATIC_ASSETS.map(url => {
                        if (url.startsWith('http')) {
                            return cache.add(new Request(url, { mode: 'no-cors' }));
                        }
                        return cache.add(url);
                    })
                );
                
                console.log('[SW] ✅ Installation réussie');
                self.skipWaiting();
            } catch (error) {
                console.error('[SW] Erreur install:', error);
            }
        })()
    );
});

// ============================================================================
// ACTIVATION - Nettoyer les anciens caches
// ============================================================================
self.addEventListener('activate', event => {
    console.log('[SW] Activation démarrée');
    
    event.waitUntil(
        (async () => {
            const cacheNames = await caches.keys();
            const whitelist = [CACHE_NAME, API_CACHE, PDF_CACHE, RUNTIME_CACHE];
            
            await Promise.all(
                cacheNames
                    .filter(name => !whitelist.includes(name))
                    .map(name => {
                        console.log('[SW] Suppression cache:', name);
                        return caches.delete(name);
                    })
            );
            
            console.log('[SW] ✅ Activation réussie');
            self.clients.claim();
        })()
    );
});

// ============================================================================
// FETCH - Stratégies intelligentes
// ============================================================================
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Ignorer non-GET
    if (request.method !== 'GET') return;
    
    // API: Network-first
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirstAPI(request));
        return;
    }
    
    // PDFs: Cache-first (critique pour offline)
    if (isPDFRequest(url)) {
        event.respondWith(cacheFirstPDF(request));
        return;
    }
    
    // Book reader: redirect to offline reader when offline
    if (url.pathname.match(/\/book\/[^/]+\/read\//)) {
        event.respondWith(handleBookReader(request, url));
        return;
    }
    
    // Offline reader pages: network-first, serve from cache offline
    if (url.pathname.startsWith('/offline-reader/')) {
        event.respondWith(networkFirstHTML(request));
        return;
    }
    
    // HTML: Network-first
    if (request.headers.get('Accept')?.includes('text/html')) {
        event.respondWith(networkFirstHTML(request));
        return;
    }
    
    // Autres assets: Cache-first
    event.respondWith(cacheFirstStatic(request));
});

// Handle book reader: try network, never force offline-reader redirect
async function handleBookReader(request, url) {
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, response.clone());
            return response;
        }
        throw new Error('Network response not ok');
    } catch (error) {
        // Keep authentication flow intact: fallback only to cached reader page.
        const cached = await caches.match(request);
        if (cached) return cached;
        
        return caches.match('/offline/').catch(() =>
            new Response('Hors-ligne', { status: 503 })
        );
    }
}

// ============================================================================
// STRATÉGIES
// ============================================================================

// Network-first pour API (données à jour en priorité)
async function networkFirstAPI(request) {
    try {
        const response = await fetch(request, { timeout: 5000 });
        
        if (response.ok) {
            const cache = await caches.open(API_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.log('[SW] API offline:', request.url);
        const cached = await caches.match(request);
        if (cached) return cached;
        
        return new Response(
            JSON.stringify({
                error: 'Mode hors-ligne',
                offline: true
            }),
            { status: 503, headers: { 'Content-Type': 'application/json' } }
        );
    }
}

// Cache-first pour PDF (important offline)
async function cacheFirstPDF(request) {
    const cached = await caches.match(request);
    if (cached) {
        console.log('[SW] PDF cached:', request.url);
        return cached;
    }
    
    try {
        const response = await fetch(request);
        
        if (response.ok) {
            const cache = await caches.open(PDF_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.error('[SW] PDF indisponible:', request.url);
        return new Response('PDF hors-ligne', { status: 503 });
    }
}

// Network-first pour HTML
async function networkFirstHTML(request) {
    try {
        const response = await fetch(request, { timeout: 5000 });
        
        if (response.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        const cached = await caches.match(request);
        if (cached) return cached;

        const frHome = await caches.match('/fr/');
        if (frHome) return frHome;

        return caches.match('/offline/').catch(() =>
            new Response('Hors-ligne', { status: 503 })
        );
    }
}

// Cache-first pour assets statiques
async function cacheFirstStatic(request) {
    const cached = await caches.match(request);
    if (cached) return cached;
    
    try {
        const response = await fetch(request);
        
        if (response.ok || response.type === 'opaque') {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        // Fallback images
        if (request.headers.get('Accept')?.includes('image')) {
            return createPlaceholderImage();
        }
        
        return new Response('Indisponible offline', { status: 503 });
    }
}

// ============================================================================
// SYNC EN ARRIÈRE-PLAN
// ============================================================================
self.addEventListener('sync', event => {
    console.log('[SW] Background sync:', event.tag);
    
    const syncHandlers = {
        'sync-reading': syncReadingSessions,
        'sync-notes': syncNotes,
        'sync-highlights': syncHighlights
    };
    
    if (event.tag in syncHandlers) {
        event.waitUntil(syncHandlers[event.tag]());
    }
});

async function syncReadingSessions() {
    try {
        const db = await getDB();
        const sessions = await getAllFromStore(db, 'readingSessions', false);
        
        for (const session of sessions) {
            try {
                const res = await fetch('/api/reading-sessions/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(session)
                });
                
                if (res.ok) {
                    session.synced = true;
                    await putInStore(db, 'readingSessions', session);
                }
            } catch (e) {
                console.error('[SW] Sync session failed:', e);
            }
        }
        
        console.log('[SW] ✅ Sessions synchronisées');
    } catch (error) {
        console.error('[SW] Sync error:', error);
    }
}

async function syncNotes() {
    console.log('[SW] Syncing notes...');
    // Implémentation similaire à syncReadingSessions
}

async function syncHighlights() {
    console.log('[SW] Syncing highlights...');
    // Implémentation similaire
}

// ============================================================================
// INDEXEDDB HELPERS
// ============================================================================
let db = null;

function getDB() {
    return new Promise((resolve, reject) => {
        if (db) return resolve(db);
        
        const req = indexedDB.open('BNC_Offline', 1);
        
        req.onupgradeneeded = e => {
            const database = e.target.result;
            ['readingSessions', 'notes', 'highlights', 'bookmarks'].forEach(store => {
                if (!database.objectStoreNames.contains(store)) {
                    database.createObjectStore(store, { keyPath: 'id' });
                }
            });
        };
        
        req.onsuccess = () => {
            db = req.result;
            resolve(db);
        };
        
        req.onerror = () => reject(req.error);
    });
}

function getAllFromStore(database, storeName, synced = null) {
    return new Promise((resolve, reject) => {
        const tx = database.transaction(storeName, 'readonly');
        const store = tx.objectStore(storeName);
        
        const req = synced === null ? store.getAll() : store.getAll();
        
        req.onsuccess = () => {
            let results = req.result;
            if (synced !== null) {
                results = results.filter(item => item.synced === synced);
            }
            resolve(results);
        };
        
        req.onerror = () => reject(req.error);
    });
}

function putInStore(database, storeName, data) {
    return new Promise((resolve, reject) => {
        const tx = database.transaction(storeName, 'readwrite');
        const store = tx.objectStore(storeName);
        const req = store.put(data);
        
        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
    });
}

// ============================================================================
// NOTIFICATIONS & MESSAGES
// ============================================================================

self.addEventListener('push', event => {
    const data = event.data?.json() ?? {};
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'BNC', {
            body: data.message || '',
            icon: '/static/images/icon-192x192.png',
            badge: '/static/images/badge.png',
            data: { url: data.url || '/' }
        })
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(clientList => {
            for (const client of clientList) {
                if (client.url === event.notification.data.url && 'focus' in client) {
                    return client.focus();
                }
            }
            return clients.openWindow?.(event.notification.data.url);
        })
    );
});

self.addEventListener('message', event => {
    const { action, data } = event.data || {};
    
    if (action === 'clearCache') {
        caches.delete(data.name).then(() => {
            event.ports[0].postMessage({ success: true });
        });
    }
    
    if (action === 'getStatus') {
        event.ports[0].postMessage({
            version: 'v2.0',
            online: navigator.onLine
        });
    }
});

// ============================================================================
// HELPERS
// ============================================================================

function isPDFRequest(url) {
    return /\.(pdf|epub)$/i.test(url.pathname) ||
           url.pathname.includes('/books/pdf/') ||
           url.pathname.includes('/books/epub/');
}

function createPlaceholderImage() {
    return new Response(
        'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x00\x00;',
        { headers: { 'Content-Type': 'image/gif' } }
    );
}

console.log('[SW] Service Worker v2.1 - Offline mode enabled');

