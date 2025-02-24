from django.urls import path
from . import views

urlpatterns = [
    path('randomize/', views.GenerateRandomFlashcards.as_view(), name='randomize'),

]