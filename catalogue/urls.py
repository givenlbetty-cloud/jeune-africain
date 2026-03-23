"""URLs pour les vues frontend."""

from django.urls import path
from . import views
from . import frontend_views
from . import payment_views
from . import recommendations_views
from . import preview_views
from . import events_views
from . import media_views
from . import forum_views

app_name = 'catalogue'

urlpatterns = [
    # Analytics
    path('analytics/', frontend_views.analytics_view, name='analytics'),
    
    # Catalogue
    path('', frontend_views.catalogue_view, name='catalogue'),
    path('book/<uuid:book_id>/', frontend_views.book_detail_view, name='book_detail'),
    path('book/<uuid:book_id>/read/', frontend_views.read_book_view, name='read_book'),
    path('book/<uuid:book_id>/order-print/', frontend_views.order_print_view, name='order_print'),
    path('book/<uuid:book_id>/update-session/', frontend_views.update_reading_session, name='update_reading_session'),
    path('book/<uuid:book_id>/purchase/', frontend_views.purchase_book_view, name='purchase_book'),
    path('book/<uuid:book_id>/simulate-purchase/', frontend_views.simulate_purchase_view, name='simulate_purchase'),
    path('book/<uuid:book_id>/update-progress/', frontend_views.update_reading_progress_view, name='update_progress'),
    path('book/<uuid:book_id>/highlight/add/', frontend_views.add_highlight_view, name='add_highlight'),
    path('book/<uuid:book_id>/highlight/list/', frontend_views.get_highlights_view, name='get_highlights'),
    path('highlight/<uuid:highlight_id>/delete/', frontend_views.delete_highlight_view, name='delete_highlight'),
    path('book/<uuid:book_id>/favorite/', frontend_views.toggle_favorite_view, name='toggle_favorite'),
    path('book/<uuid:book_id>/review/', frontend_views.add_review_view, name='add_review'),
    path('author/<uuid:author_id>/', frontend_views.author_detail_view, name='author_detail'),
    
    # Événements
    path('events/', frontend_views.events_view, name='events_list'),
    path('event/<uuid:event_id>/', frontend_views.event_detail_view, name='event_detail'),
    
    # Recommandations
    path('recommendations/', recommendations_views.recommendations_view, name='recommendations'),
    path('recommendations/dashboard/', frontend_views.recommendations_dashboard, name='recommendations_dashboard'),
    path('api/recommendations/', recommendations_views.recommendations_api_view, name='recommendations_api'),
    
    # Paiement
    path('payment/<uuid:book_id>/initiate/', payment_views.initiate_payment_view, name='initiate_payment'),
    path('payment/<uuid:payment_id>/success/', payment_views.payment_success_view, name='payment_success'),
    path('payment/<uuid:payment_id>/cancel/', payment_views.payment_cancel_view, name='payment_cancel'),
    path('payment/history/', payment_views.payment_history_view, name='payment_history'),
    path('payment/webhook/orange/', payment_views.payment_webhook_orange, name='webhook_orange'),
    path('payment/webhook/stripe/', payment_views.payment_webhook_stripe, name='webhook_stripe'),
    
    # ✨ Mobile Money Payment
    path('api/payments/mobile-money/<uuid:book_id>/', payment_views.initiate_mobile_money_payment_view, name='initiate_mobile_money'),
    path('api/payments/mobile-money/<uuid:payment_id>/status/', payment_views.check_mobile_money_status_view, name='check_mobile_money_status'),
    path('api/payments/webhook/mpesa/', payment_views.mpesa_webhook, name='webhook_mpesa'),
    path('api/payments/webhook/airtel/', payment_views.airtel_webhook, name='webhook_airtel'),
    path('api/payments/webhook/orange/', payment_views.orange_webhook, name='webhook_orange_money'),
    
    # ✨ Free Preview System
    path('api/book/<uuid:book_id>/can-read/', preview_views.can_read_full_book_view, name='can_read_full_book'),
    path('api/book/<uuid:book_id>/preview-pages/', preview_views.get_free_preview_pages_view, name='get_preview_pages'),
    path('api/book/<uuid:book_id>/page/<int:page_number>/access/', preview_views.check_page_access_view, name='check_page_access'),
    
    # ✨ Events & Announcements API
    path('api/events/', events_views.events_list_api_view, name='api_events_list'),
    path('api/events/create/', events_views.create_event_api_view, name='api_create_event'),
    path('api/events/<uuid:event_id>/', events_views.event_detail_api_view, name='api_event_detail'),
    path('api/events/<uuid:event_id>/register/', events_views.register_event_api_view, name='api_register_event'),
    path('api/events/<uuid:event_id>/unregister/', events_views.unregister_event_api_view, name='api_unregister_event'),
    path('api/events/my-registrations/', events_views.my_registrations_api_view, name='api_my_registrations'),
    path('api/events/upcoming/', events_views.upcoming_events_api_view, name='api_upcoming_events'),
    path('api/events/<uuid:event_id>/stats/', events_views.event_stats_api_view, name='api_event_stats'),
    
    # ✨ Annotations (Highlights & Notes)
    path('book/<uuid:book_id>/annotations/', frontend_views.get_annotations_view, name='get_annotations'),
    path('book/<uuid:book_id>/highlight/', frontend_views.save_highlight_view, name='save_highlight'),
    path('book/<uuid:book_id>/highlight/<uuid:highlight_id>/delete/', frontend_views.delete_highlight_view, name='delete_highlight'),
    path('book/<uuid:book_id>/note/', frontend_views.save_note_view, name='save_note'),
    path('book/<uuid:book_id>/note/<uuid:note_id>/delete/', frontend_views.delete_note_view, name='delete_note'),
    path('book/<uuid:book_id>/annotations/export/', frontend_views.export_annotations_view, name='export_annotations'),
    
    # Legacy API routes
    path('api/book/<uuid:book_id>/annotations/', frontend_views.get_annotations_view, name='api_get_annotations'),
    path('api/book/<uuid:book_id>/highlights/add/', frontend_views.add_highlight_view, name='api_add_highlight'),
    path('api/book/<uuid:book_id>/notes/add/', frontend_views.add_note_view, name='api_add_note'),
    
    # ✨ PHASE 9: Médias (Audiobooks, Vidéos, Podcasts)
    
    # Audiobooks
    path('audiobooks/', media_views.audiobooks_view, name='audiobooks_list'),
    path('audiobook/<uuid:book_id>/', media_views.audiobook_detail_view, name='audiobook_detail'),
    path('audiobook/<uuid:book_id>/play/', media_views.audiobook_player_view, name='audiobook_player'),
    path('api/audiobooks/', media_views.audiobooks_api_view, name='audiobooks_api'),
    
    # Vidéos
    path('videos/', media_views.videos_view, name='videos_list'),
    path('video/<uuid:video_id>/', media_views.video_detail_view, name='video_detail'),
    path('video/<uuid:video_id>/progress/', media_views.update_video_progress_view, name='update_video_progress'),
    path('api/videos/', media_views.videos_api_view, name='videos_api'),
    
    # Podcasts
    path('podcasts/', media_views.podcasts_view, name='podcasts_list'),
    path('podcast/<uuid:podcast_id>/', media_views.podcast_detail_view, name='podcast_detail'),
    path('podcast/<uuid:podcast_id>/subscribe/', media_views.toggle_podcast_subscription_view, name='toggle_podcast_subscription'),
    path('podcast/<uuid:podcast_id>/episode/<uuid:episode_id>/', media_views.podcast_episode_detail_view, name='podcast_episode_detail'),
    path('podcast/episode/<uuid:episode_id>/progress/', media_views.update_podcast_progress_view, name='update_podcast_progress'),
    path('api/podcasts/', media_views.podcasts_api_view, name='podcasts_api'),
    
    # ✨ PHASE 7: Forum Communautaire
    
    # Categories
    path('forum/', forum_views.forum_categories_view, name='forum_home'),
    path('forum/categories/', forum_views.forum_categories_view, name='forum_categories'),
    path('forum/category/<uuid:category_id>/', forum_views.forum_category_detail_view, name='forum_category_detail'),
    
    # Discussions/Threads
    path('forum/discussions/', forum_views.forum_threads_view, name='forum_threads'),
    path('forum/discussion/<uuid:thread_id>/', forum_views.forum_thread_detail_view, name='forum_thread_detail'),
    path('forum/create/', forum_views.create_forum_thread_view, name='create_forum_thread'),
    path('forum/thread/<uuid:thread_id>/edit/', forum_views.edit_forum_thread_view, name='edit_forum_thread'),
    path('forum/thread/<uuid:thread_id>/delete/', forum_views.delete_forum_thread_view, name='delete_forum_thread'),
    
    # Replies/Commentaires
    path('forum/thread/<uuid:thread_id>/reply/', forum_views.reply_to_thread_view, name='reply_to_thread'),
    path('forum/reply/<uuid:reply_id>/edit/', forum_views.edit_forum_reply_view, name='edit_forum_reply'),
    path('forum/reply/<uuid:reply_id>/delete/', forum_views.delete_forum_reply_view, name='delete_forum_reply'),
    
    # Votes
    path('forum/thread/<uuid:thread_id>/vote/', forum_views.vote_thread_view, name='vote_thread'),
    path('forum/reply/<uuid:reply_id>/vote/', forum_views.vote_reply_view, name='vote_reply'),
    
    # API
    path('api/forum/', forum_views.forum_api_view, name='forum_api'),
    path('api/forum/categories/', forum_views.forum_categories_api_view, name='forum_categories_api'),
]

