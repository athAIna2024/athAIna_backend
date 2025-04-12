from django.urls import path
from . import views

urlpatterns = [
    path('', views.ListOfFlashcards.as_view(), name='list_flashcards'),
    path('save/', views.CreateFlashcard.as_view(), name='create_flashcard'),
    path('library/', views.LibraryOfFlashcards.as_view(), name='library_flashcards'),
    path('review_mode/', views.ReviewModeFlashcard.as_view(), name='review_flashcards'),
    path('update/<int:id>/', views.UpdateFlashcard.as_view(), name='update_flashcard'),
    path('delete/<int:id>/', views.DeleteFlashcard.as_view(), name='delete_flashcard'),
    path('search/', views.FlashcardSearchView.as_view(), name='flashcard_search'),

]