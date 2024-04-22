# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import UserRegistrationViewSet, AuthViewSet, DeckViewSet, FlashcardViewSet
# #register, home, login

# router = DefaultRouter()
# router.register(r'signup', UserRegistrationViewSet, basename='users')
# #router.register(r'login', AuthViewSet, basename='auth')
# router.register(r'decks', DeckViewSet)
# router.register(r'flashcards', FlashcardViewSet, basename='flashcards')
# #router.register(r'decks/(?P<deck_pk>[^/.]+)/flashcards', FlashcardViewSet, basename='deck-flashcards')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),
# ]

# urlpatterns = [
#     path('signup/', register, name='signup'),
#     path('login/', login, name='login'),
#     path('', home, name='home')
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import UserRegistrationViewSet, AuthViewSet, DeckViewSet, FlashcardViewSet, UserStreakView, FlashcardReviewView, UserDecksView, DeckFlashcardsView, FlashcardRatingView

# Main router
router = DefaultRouter()
router.register(r'signup', UserRegistrationViewSet, basename='users')
router.register(r'decks', DeckViewSet)  # Main endpoint for decks

# Nested router for flashcards under decks
deck_router = NestedDefaultRouter(router, r'decks', lookup='deck')
deck_router.register(r'flashcards', FlashcardViewSet, basename='deck-flashcards')

urlpatterns = [
    path('', include(router.urls)),  # Main routes
    path('', include(deck_router.urls)),  # Nested routes
    path('login/', AuthViewSet.as_view({'post': 'login'}), name='login'),  # Custom login
    path('user/streak/', UserStreakView.as_view(), name='user-streak'),   # URL endpoint for user streak
    #path('flashcards/review/', FlashcardReviewView.as_view(), name='flashcard-review'),
    # User-specific decks
    path('user/decks/', UserDecksView.as_view(), name='user-decks'),

    # Flashcards in a specific deck
    path('decks/<int:deck_id>/flashcards/', DeckFlashcardsView.as_view(), name='deck-flashcards'),

    # Update spaced repetition based on a flashcard's rating
    path('flashcards/rate/', FlashcardRatingView.as_view(), name='flashcard-rate'),
]
