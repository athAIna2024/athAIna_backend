from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'create', views.CreateFlashcard, basename='create_flashcard')
router.register(r'list', views.ListOfFlashcards, basename='list_flashcards')
router.register(r'library', views.LibraryOfFlashcards, basename='library_flashcards')
router.register(r'review_mode', views.ReviewModeFlashcard, basename='review_flashcards')
router.register(r'update', views.UpdateFlashcard, basename='update_flashcard')
router.register(r'delete', views.DeleteFlashcard, basename='delete_flashcard')

urlpatterns = [
    path('', include(router.urls)),
]