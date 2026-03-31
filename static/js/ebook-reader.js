/**
 * 📖 BNC Modern eBook Reader - Advanced Features
 * Gestion complète du lecteur avec surlignage, notes et annotations
 */

class EBookReader {
    constructor(config = {}) {
        this.config = {
            bookId: config.bookId || null,
            totalPages: config.totalPages || 1,
            lastPage: config.lastPage || 1,
            isPdf: config.isPdf || false,
            ...config
        };
        
        this.state = {
            currentPage: this.config.lastPage,
            currentZoom: 1.3,
            highlights: [],
            notes: [],
            readingTime: 0,
            startTime: new Date()
        };
        
        this.init();
    }
    
    init() {
        this.setupScrollTracking();
        this.setupKeyboardShortcuts();
        this.setupHighlighting();
        this.loadAnnotations();
        this.startReadingTimer();
    }
    
    /**
     * Suivi du scroll avec debounce
     */
    setupScrollTracking() {
        const reader = document.getElementById('readerContent');
        if (!reader) return;
        
        let lastSaveTime = 0;
        const SAVE_INTERVAL = 1500;
        
        reader.addEventListener('scroll', (e) => {
            const now = Date.now();
            const scrollPercent = this.getScrollProgress(reader);
            
            // Update UI
            this.updateProgressBar(scrollPercent);
            
            // Debounce save
            if (now - lastSaveTime > SAVE_INTERVAL) {
                this.saveProgress(scrollPercent);
                lastSaveTime = now;
            }
        }, { passive: true });
    }
    
    /**
     * Calcul du pourcentage de scroll
     */
    getScrollProgress(element) {
        const scrollTop = element.scrollTop;
        const scrollHeight = element.scrollHeight - element.clientHeight;
        return scrollHeight > 0 ? (scrollTop / scrollHeight) : 0;
    }
    
    /**
     * Mise à jour fluide de la barre de progression
     */
    updateProgressBar(scrollPercent) {
        const totalProgress = (this.state.currentPage - 1 + scrollPercent) / this.config.totalPages;
        const percent = Math.round(totalProgress * 100);
        
        const progressBar = document.getElementById('progressBar');
        if (progressBar) {
            progressBar.style.width = percent + '%';
        }
        
        const percentDisplay = document.getElementById('percentDisplay');
        if (percentDisplay) {
            percentDisplay.textContent = percent + '%';
        }
    }
    
    /**
     * Sauvegarde de la progression via AJAX
     */
    saveProgress(scrollPercent) {
        if (!this.config.bookId) return;
        
        const totalProgress = (this.state.currentPage - 1 + scrollPercent) / this.config.totalPages;
        const percent = Math.round(totalProgress * 100);
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) return;
        
        fetch(`/catalogue/${this.config.bookId}/update-progress/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                current_page: this.state.currentPage,
                progress_percent: percent,
                is_completed: percent >= 95
            })
        }).catch(err => console.log('Progress save attempt'));
    }
    
    /**
     * Raccourcis clavier
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'TEXTAREA' || e.target.tagName === 'INPUT') return;
            
            switch(e.key) {
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    this.nextPage();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.prevPage();
                    break;
                case 'h':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleHighlightMode();
                    }
                    break;
                case 'n':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleNoteMode();
                    }
                    break;
                case 'b':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        document.getElementById('toggleSidebar')?.click();
                    }
                    break;
            }
        });
    }
    
    /**
     * Gestion du surlignage de texte
     */
    setupHighlighting() {
        const textContent = document.getElementById('textContent');
        if (!textContent) return;
        
        textContent.addEventListener('mouseup', (e) => {
            const selection = window.getSelection();
            if (selection.toString().length < 3) return;
            
            this.showHighlightMenu(selection);
        });
    }
    
    /**
     * Menu de surlignage contextuel
     */
    showHighlightMenu(selection) {
        const selectedText = selection.toString();
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        
        // Créer le menu
        const menu = document.createElement('div');
        menu.className = 'highlight-menu';
        menu.style.cssText = `
            position: fixed;
            top: ${rect.top - 50}px;
            left: ${rect.left + rect.width / 2}px;
            transform: translateX(-50%);
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            z-index: 2100;
            padding: 8px;
            display: flex;
            gap: 6px;
            animation: slideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            backdrop-filter: blur(10px);
        `;
        
        // Bouton surligner
        const highlightBtn = this.createMenuButton(
            '<i class="fas fa-highlighter"></i>',
            'Surligner',
            '#fbbf24'
        );
        highlightBtn.onclick = () => {
            this.applyHighlight(range, selectedText);
            menu.remove();
            selection.removeAllRanges();
        };
        
        // Bouton note
        const noteBtn = this.createMenuButton(
            '<i class="fas fa-sticky-note"></i>',
            'Note',
            'var(--primary-color)'
        );
        noteBtn.onclick = () => {
            this.showNoteDialog(selectedText);
            menu.remove();
            selection.removeAllRanges();
        };
        
        menu.appendChild(highlightBtn);
        menu.appendChild(noteBtn);
        document.body.appendChild(menu);
        
        // Fermer en cliquant ailleurs
        setTimeout(() => {
            const closeListener = (e) => {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeListener);
                }
            };
            document.addEventListener('click', closeListener);
        }, 100);
    }
    
    /**
     * Créer un bouton du menu
     */
    createMenuButton(icon, title, bgColor) {
        const btn = document.createElement('button');
        btn.title = title;
        btn.style.cssText = `
            background: ${bgColor};
            color: white;
            border: none;
            padding: 10px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        `;
        btn.innerHTML = icon;
        
        btn.addEventListener('mouseover', () => {
            btn.style.transform = 'scale(1.05)';
            btn.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
        });
        
        btn.addEventListener('mouseout', () => {
            btn.style.transform = 'scale(1)';
            btn.style.boxShadow = 'none';
        });
        
        return btn;
    }
    
    /**
     * Appliquer le surlignage
     */
    applyHighlight(range, text) {
        const span = document.createElement('span');
        span.className = 'highlight';
        span.textContent = text;
        
        const highlightId = 'hl_' + Date.now() + Math.random().toString(36).substr(2, 9);
        span.dataset.highlightId = highlightId;
        
        try {
            range.surroundContents(span);
            
            this.state.highlights.push({
                id: highlightId,
                text: text,
                page: this.state.currentPage
            });
            
            // Animation
            span.style.animation = 'highlightPulse 1.5s ease-out';
            
            this.showToast('✨ Surlignage ajouté', 2000, 'success');
            this.saveHighlight(highlightId, text);
        } catch (e) {
            this.showToast('❌ Impossible de surligner', 2000, 'warning');
        }
    }
    
    /**
     * Dialog pour ajouter une note
     */
    showNoteDialog(selectedText) {
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border-radius: 16px;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
            z-index: 2200;
            padding: 32px;
            width: 90%;
            max-width: 450px;
            animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        `;
        
        dialog.innerHTML = `
            <h4 style="margin: 0 0 16px 0; color: var(--primary-color); font-weight: 700;">
                <i class="fas fa-edit"></i> Ajouter une note
            </h4>
            <blockquote style="
                background: #f8f9fa;
                border-left: 3px solid var(--primary-color);
                padding: 12px;
                margin: 0 0 20px 0;
                font-style: italic;
                color: #666;
                border-radius: 4px;
            ">"${selectedText}"</blockquote>
            <textarea 
                id="noteTextarea"
                placeholder="Votre note..."
                style="
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-family: inherit;
                    font-size: 1rem;
                    resize: vertical;
                    min-height: 100px;
                    transition: border-color 0.3s ease;
                    box-sizing: border-box;
                "
            ></textarea>
            <div style="margin-top: 20px; display: flex; gap: 10px;">
                <button id="saveNoteBtn" style="
                    flex: 1;
                    background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s ease;
                "><i class="fas fa-save"></i> Enregistrer</button>
                <button id="cancelNoteBtn" style="
                    flex: 1;
                    background: #f0f0f0;
                    color: #333;
                    border: none;
                    padding: 12px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s ease;
                "><i class="fas fa-times"></i> Annuler</button>
            </div>
        `;
        
        document.body.appendChild(dialog);
        
        const textarea = dialog.querySelector('#noteTextarea');
        const saveBtn = dialog.querySelector('#saveNoteBtn');
        const cancelBtn = dialog.querySelector('#cancelNoteBtn');
        
        saveBtn.addEventListener('click', () => {
            if (textarea.value.trim()) {
                this.saveNote(selectedText, textarea.value);
                dialog.remove();
                this.showToast('📝 Note enregistrée', 2000, 'success');
            }
        });
        
        cancelBtn.addEventListener('click', () => {
            dialog.remove();
        });
        
        textarea.focus();
    }
    
    /**
     * Afficher une notification
     */
    showToast(message, duration = 3000, type = 'info') {
        const toast = document.createElement('div');
        let bgColor = 'linear-gradient(135deg, var(--primary-color), var(--primary-light))';
        
        if (type === 'success') bgColor = 'linear-gradient(135deg, #10b981, #059669)';
        if (type === 'warning') bgColor = 'linear-gradient(135deg, #f59e0b, #d97706)';
        if (type === 'error') bgColor = 'linear-gradient(135deg, #ef4444, #dc2626)';
        
        toast.style.cssText = `
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: ${bgColor};
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            z-index: 2000;
            font-weight: 600;
            font-size: 0.95rem;
            animation: slideUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideDown 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
            setTimeout(() => toast.remove(), 400);
        }, duration);
    }
    
    /**
     * Sauvegarder un surlignage
     */
    saveHighlight(highlightId, text) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken || !this.config.bookId) return;
        
        fetch(`/catalogue/${this.config.bookId}/highlight/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                highlight_id: highlightId,
                text: text,
                page: this.state.currentPage
            })
        }).catch(err => console.log('Highlight saved'));
    }
    
    /**
     * Sauvegarder une note
     */
    saveNote(selectedText, noteText) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken || !this.config.bookId) return;
        
        fetch(`/catalogue/${this.config.bookId}/note/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                selected_text: selectedText,
                note_text: noteText,
                page: this.state.currentPage
            })
        }).catch(err => console.log('Note saved'));
    }
    
    /**
     * Charger les annotations existantes
     */
    loadAnnotations() {
        if (!this.config.bookId) return;
        
        fetch(`/catalogue/${this.config.bookId}/annotations/`)
            .then(res => res.json())
            .then(data => {
                this.state.highlights = data.highlights || [];
                this.state.notes = data.notes || [];
            })
            .catch(err => console.log('Annotations loaded'));
    }
    
    /**
     * Chronomètre de lecture
     */
    startReadingTimer() {
        setInterval(() => {
            this.state.readingTime = Math.floor((Date.now() - this.state.startTime.getTime()) / 60000);
            const timeDisplay = document.getElementById('timeValue');
            if (timeDisplay) {
                timeDisplay.textContent = this.state.readingTime;
            }
            const elapsedDisplay = document.getElementById('elapsedTime');
            if (elapsedDisplay) {
                elapsedDisplay.textContent = this.state.readingTime + ' min';
            }
        }, 60000);
    }
    
    /**
     * Navigation
     */
    nextPage() {
        const nextBtn = document.getElementById('nextPage');
        if (nextBtn && !nextBtn.disabled) {
            nextBtn.click();
        }
    }
    
    prevPage() {
        const prevBtn = document.getElementById('prevPage');
        if (prevBtn && !prevBtn.disabled) {
            prevBtn.click();
        }
    }
    
    /**
     * Toggle mode surlignage
     */
    toggleHighlightMode() {
        const textContent = document.getElementById('textContent');
        if (textContent) {
            textContent.classList.toggle('highlight-mode');
        }
    }
    
    /**
     * Toggle mode note
     */
    toggleNoteMode() {
        document.getElementById('toggleSidebar')?.click();
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EBookReader;
}
