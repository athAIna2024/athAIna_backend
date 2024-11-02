from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateFlashcard.as_view(), name='create_flashcard'),
    path('library_flashcards/', views.LibraryOfFlashcards.as_view(), name='library_flashcards'),
    path('review_flashcards/', views.ReviewModeFlashcard.as_view(), name='review_flashcards'),
    path('update/<int:id>/', views.UpdateFlashcard.as_view(), name='update_flashcard'),

    path('delete/<int:id>/', views.DeleteFlashcard.as_view(), name='delete_flashcard'),
]