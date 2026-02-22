/**
 * BNC - Optimisations et fonctionnalités additionnelles
 * Corrections #5 (navigation footer), #6 (screenshots), #9 (performance)
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // =======================================
    // CORRECTION #5: Navigation Footer
    // =======================================
    
    const scrollTopBtn = document.getElementById('scroll-top-btn');
    
    if (scrollTopBtn) {
        // Afficher/masquer le bouton selon le scroll
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('show');
                scrollTopBtn.classList.remove('d-none');
            } else {
                scrollTopBtn.classList.remove('show');
                scrollTopBtn.classList.add('d-none');
            }
        });
        
        // Scroll fluide vers le haut
        scrollTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
            
            // CORRECTION UI: Feedback visuel
            scrollTopBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                scrollTopBtn.style.transform = 'scale(1)';
            }, 100);
        });
    }
    
    
    // =======================================
    // CORRECTION #6: Captures d'écran
    // =======================================
    
    const screenshotBtn = document.getElementById('screenshot-btn');
    
    if (screenshotBtn) {
        // Vérifier que html2canvas est disponible
        if (typeof html2canvas === 'undefined') {
            console.warn('html2canvas non chargé - fonction screenshot désactivée');
            screenshotBtn.disabled = true;
            screenshotBtn.title = 'html2canvas non disponible';
        } else {
            screenshotBtn.addEventListener('click', async function(e) {
                e.preventDefault();
                
                const element = document.querySelector('.book-reader') || 
                               document.querySelector('.book-content') ||
                               document.querySelector('.card');
                
                if (!element) {
                    alert('❌ Zone à capturer non trouvée');
                    return;
                }
                
                // Désactiver le bouton pendant la capture
                const originalText = screenshotBtn.innerHTML;
                screenshotBtn.disabled = true;
                screenshotBtn.innerHTML = '<span class="spinner-border spinner-border-sm mr-2"></span>Capture en cours...';
                
                try {
                    const canvas = await html2canvas(element, {
                        scale: 2,
                        backgroundColor: '#ffffff',
                        allowTaint: true,
                        useCORS: true,
                    });
                    
                    // Télécharger l'image
                    const link = document.createElement('a');
                    link.href = canvas.toDataURL('image/png');
                    
                    const bookTitle = document.querySelector('h1')?.textContent || 'Capture';
                    link.download = `${bookTitle}-${new Date().getTime()}.png`;
                    
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    // Feedback succès
                    const originalClass = screenshotBtn.className;
                    screenshotBtn.className = 'btn btn-success';
                    screenshotBtn.innerHTML = '<i class="fas fa-check"></i> Capture téléchargée!';
                    
                    setTimeout(() => {
                        screenshotBtn.className = originalClass;
                        screenshotBtn.innerHTML = originalText;
                        screenshotBtn.disabled = false;
                    }, 2000);
                    
                } catch (error) {
                    console.error('Erreur lors de la capture:', error);
                    alert('❌ Erreur lors de la capture: ' + error.message);
                    screenshotBtn.disabled = false;
                    screenshotBtn.innerHTML = originalText;
                }
            });
        }
    }
    
    
    // =======================================
    // CORRECTION #9: Optimisations Performance
    // =======================================
    
    // 1. Images lazy-loading
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                    }
                    observer.unobserve(img);
                }
            });
        });
        
        // Observer toutes les images avec data-src
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // 2. Dédupliquer les event listeners (éviter les fuites mémoire)
    const lazyElements = document.querySelectorAll('[data-lazy-load]');
    lazyElements.forEach(el => {
        if (!el.dataset.lazyLoaded) {
            el.dataset.lazyLoaded = true;
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('loaded');
                        observer.unobserve(entry.target);
                    }
                });
            });
            observer.observe(el);
        }
    });
    
    // 3. Debounce pour resize events
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            // Recalculer layouts si nécessaire
            document.dispatchEvent(new Event('bnc-window-resized'));
        }, 250);
    });
    
    // 4. Log des performances (si DEBUG)
    if (document.querySelector('body').dataset.debug === 'true') {
        window.addEventListener('load', function() {
            if (window.performance && window.performance.timing) {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                console.log(`⏱️  Temps de chargement: ${pageLoadTime}ms`);
            }
        });
    }
    
});

// =======================================
// Utilitaire: Fonction pour tracker les actions
// =======================================

window.BNCTracking = {
    trackEvent: function(category, action, label) {
        'use strict';
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                'event_category': category,
                'event_label': label
            });
        } else {
            console.log(`📊 Event: ${category} > ${action} > ${label}`);
        }
    }
};
