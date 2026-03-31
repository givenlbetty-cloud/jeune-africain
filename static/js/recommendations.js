/**
 * Recommendations Module - Updated for API Format
 * Handles loading and displaying book recommendations from the API
 */

const RecommendationsModule = {
    // Configuration
    config: {
        limitPerSection: 6,
        trendingDays: 7,
        bestRatedMinRating: 3.5,
    },

    // Initialize the module
    init: function() {
        this.loadPersonalizedRecommendations();
        this.loadTrendingBooks();
        this.loadBestRatedBooks();
    },

    /**
     * Load personalized recommendations for authenticated users
     */
    loadPersonalizedRecommendations: function() {
        const container = document.getElementById('personalized-recommendations');
        if (!container) return;

        fetch(`/api/books/recommendations/?limit=${this.config.limitPerSection}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to load recommendations');
                return response.json();
            })
            .then(data => {
                if (data.books && data.books.length > 0) {
                    this.renderRecommendationCards(container, data.books);
                } else {
                    container.innerHTML = '<div class="col-12"><p class="text-muted text-center">Aucune recommandation disponible pour le moment.</p></div>';
                }
            })
            .catch(error => {
                console.error('Error loading personalized recommendations:', error);
                container.innerHTML = '<div class="col-12"><p class="text-danger text-center">Erreur lors du chargement des recommandations.</p></div>';
            });
    },

    /**
     * Load trending books
     */
    loadTrendingBooks: function() {
        const container = document.getElementById('trending-recommendations');
        if (!container) return;

        fetch(`/api/books/trending/?days=${this.config.trendingDays}&limit=${this.config.limitPerSection}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to load trending books');
                return response.json();
            })
            .then(data => {
                if (data.books && data.books.length > 0) {
                    this.renderTrendingCards(container, data.books);
                } else {
                    container.innerHTML = '<div class="col-12"><p class="text-muted text-center">Aucun livre tendance pour le moment.</p></div>';
                }
            })
            .catch(error => {
                console.error('Error loading trending books:', error);
                container.innerHTML = '<div class="col-12"><p class="text-danger text-center">Erreur lors du chargement des livres tendance.</p></div>';
            });
    },

    /**
     * Load best rated books
     */
    loadBestRatedBooks: function() {
        const container = document.getElementById('best-rated-recommendations');
        if (!container) return;

        fetch(`/api/books/best_rated/?min_rating=${this.config.bestRatedMinRating}&limit=${this.config.limitPerSection}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to load best rated books');
                return response.json();
            })
            .then(data => {
                if (data.books && data.books.length > 0) {
                    this.renderBestRatedCards(container, data.books);
                } else {
                    container.innerHTML = '<div class="col-12"><p class="text-muted text-center">Aucun livre bien noté pour le moment.</p></div>';
                }
            })
            .catch(error => {
                console.error('Error loading best rated books:', error);
                container.innerHTML = '<div class="col-12"><p class="text-danger text-center">Erreur lors du chargement des meilleures notes.</p></div>';
            });
    },

    /**
     * Render personalized recommendation cards
     */
    renderRecommendationCards: function(container, books) {
        let html = '';
        
        books.forEach(book => {
            const coverUrl = book.cover || '/static/images/placeholder-book.png';
            const rating = parseFloat(book.rating || 0).toFixed(1);
            const authors = this.getAuthorsString(book.author_books);
            
            html += `
                <div class="col-md-4 col-lg-2 col-sm-6">
                    <div class="recommendation-card">
                        <div class="recommendation-card-img">
                            <img src="${coverUrl}" alt="${book.title}" onerror="this.src='/static/images/placeholder-book.png'">
                            <span class="recommendation-reason">
                                <i class="fas fa-thumbs-up"></i> Recommandé
                            </span>
                        </div>
                        <div class="recommendation-card-body">
                            <h6 class="recommendation-card-title">
                                <a href="/fr/books/book/${book.id}/">${book.title}</a>
                            </h6>
                            <p class="recommendation-card-author">
                                ${authors}
                            </p>
                            <div class="recommendation-card-rating">
                                ${this.renderStars(rating)}
                                <span class="ms-2">${rating}/5</span>
                            </div>
                            <div class="recommendation-card-meta">
                                <span>${book.pages_count || 0} pages</span>
                            </div>
                            <div class="recommendation-card-action mt-3">
                                <a href="/fr/books/book/${book.id}/" class="btn btn-sm btn-primary w-100">
                                    <i class="fas fa-eye"></i> Voir
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    },

    /**
     * Render trending book cards
     */
    renderTrendingCards: function(container, books) {
        let html = '';
        
        books.forEach((book, index) => {
            const coverUrl = book.cover || '/static/images/placeholder-book.png';
            const rating = parseFloat(book.rating || 0).toFixed(1);
            const authors = this.getAuthorsString(book.author_books);
            
            html += `
                <div class="col-md-4 col-lg-2 col-sm-6">
                    <div class="recommendation-card">
                        <div class="recommendation-card-img">
                            <img src="${coverUrl}" alt="${book.title}" onerror="this.src='/static/images/placeholder-book.png'">
                            <span class="recommendation-trending-badge">
                                #${index + 1} <i class="fas fa-flame"></i>
                            </span>
                        </div>
                        <div class="recommendation-card-body">
                            <h6 class="recommendation-card-title">
                                <a href="/fr/books/book/${book.id}/">${book.title}</a>
                            </h6>
                            <p class="recommendation-card-author">
                                ${authors}
                            </p>
                            <div class="recommendation-card-rating">
                                ${this.renderStars(rating)}
                                <span class="ms-2">${rating}/5</span>
                            </div>
                            <div class="recommendation-card-meta">
                                <span>
                                    <i class="fas fa-users"></i> ${book.rating_count || 0} avis
                                </span>
                            </div>
                            <div class="recommendation-card-action mt-3">
                                <a href="/fr/books/book/${book.id}/" class="btn btn-sm btn-primary w-100">
                                    <i class="fas fa-eye"></i> Voir
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    },

    /**
     * Render best rated book cards
     */
    renderBestRatedCards: function(container, books) {
        let html = '';
        
        books.forEach((book, index) => {
            const coverUrl = book.cover || '/static/images/placeholder-book.png';
            const rating = parseFloat(book.rating || 0).toFixed(1);
            const authors = this.getAuthorsString(book.author_books);
            
            html += `
                <div class="col-md-4 col-lg-2 col-sm-6">
                    <div class="recommendation-card">
                        <div class="recommendation-card-img">
                            <img src="${coverUrl}" alt="${book.title}" onerror="this.src='/static/images/placeholder-book.png'">
                            <span class="recommendation-reason">
                                <i class="fas fa-star"></i> ${rating}/5
                            </span>
                        </div>
                        <div class="recommendation-card-body">
                            <h6 class="recommendation-card-title">
                                <a href="/fr/books/book/${book.id}/">${book.title}</a>
                            </h6>
                            <p class="recommendation-card-author">
                                ${authors}
                            </p>
                            <div class="recommendation-card-rating">
                                ${this.renderStars(rating)}
                                <span class="ms-2">${rating}/5</span>
                            </div>
                            <div class="recommendation-card-meta">
                                <span>
                                    <i class="fas fa-comments"></i> ${book.rating_count || 0} avis
                                </span>
                            </div>
                            <div class="recommendation-card-action mt-3">
                                <a href="/fr/books/book/${book.id}/" class="btn btn-sm btn-primary w-100">
                                    <i class="fas fa-eye"></i> Voir
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    },

    /**
     * Get authors string from author_books array
     */
    getAuthorsString: function(authorBooks) {
        if (!authorBooks || authorBooks.length === 0) {
            return 'Auteur inconnu';
        }
        return authorBooks.map(ab => {
            const author = ab.author;
            return author.first_name + ' ' + author.last_name;
        }).join(', ');
    },

    /**
     * Render star rating
     */
    renderStars: function(rating) {
        let html = '';
        const roundedRating = Math.round(rating);
        
        for (let i = 1; i <= 5; i++) {
            if (i <= roundedRating) {
                html += '<i class="fas fa-star"></i>';
            } else if (i - rating < 1 && i - rating > 0) {
                html += '<i class="fas fa-star-half-alt"></i>';
            } else {
                html += '<i class="far fa-star"></i>';
            }
        }
        
        return html;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    RecommendationsModule.init();
});
