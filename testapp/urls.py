from django.urls import path
from . import views

urlpatterns = [
    path('generate_random_flashcards/', views.GenerateRandomFlashcards.as_view(), name='generate_random_flashcards'),
    path('process-generated-tests/', views.NoBackTracking.as_view(), name='process-generated-tests'),
    path('validate-learner-answer/', views.LearnerAnswerValidation.as_view(), name='validate_learner_answer'),
    path('summary-of-scores/', views.SaveTestResults.as_view(), name='summary_of_scores'),
]