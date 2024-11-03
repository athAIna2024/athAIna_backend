from django.urls import path
from . import views

urlpatterns = [
    path('generate_random_flashcards/', views.GenerateRandomFlashcards.as_view(), name='generate_random_flashcards'),
    path('<uuid:batch_id>/', views.NoBackTracking.as_view(), name='process-generated-tests'),
]

