from django.urls import path
from . import views

urlpatterns = [
    path('randomize/', views.GenerateRandomFlashcards.as_view(), name='randomize'),
    path('validate_learner_answer/<int:id>/', views.ValidateLearnerAnswerWithAi.as_view(), name='validate_learner_answer'),

]