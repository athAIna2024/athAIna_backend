from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'generate_random_flashcards', views.GenerateRandomFlashcards, basename='generate_random_flashcards')
router.register(r'process-generated-tests', views.NoBackTracking, basename='process-generated-tests')
router.register(r'validate-learner-answer', views.LearnerAnswerValidation, basename='validate-learner-answer')
router.register(r'summary-of-scores', views.SaveTestResults, basename='summary-of-scores')

urlpatterns = [
    path('', include(router.urls)),
]