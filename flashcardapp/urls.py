from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateFlashcard.as_view(), name='create_flashcard'),
    path('list/', views.ListFlashcard.as_view(), name='list_flashcard'),
    path('update/<int:id>/', views.UpdateFlashcard.as_view(), name='update_flashcard'),

    path('delete/<int:id>/', views.DeleteFlashcard.as_view(), name='delete_flashcard'),
]