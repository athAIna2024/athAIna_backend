from django.urls import path
from . import views

urlpatterns = [
    path('generate_random_flashcards/', views.GenerateRandomFlashcards.as_view(), name='generate_random_flashcards'),
    path('<uuid:batch_id>/', views.NoBackTracking.as_view(), name='process-generated-tests'),
    path('<uuid:batch_id>/<int:flashcard_instance>/', views.LearnerAnswerValidation.as_view(), name='validate-learner-answer'),
    path('<uuid:batch_id>/summary_of_scores/', views.SaveTestResults.as_view(), name='summary-of-scores'),

]