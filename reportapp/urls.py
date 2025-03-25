from django.urls import path
from . import views

urlpatterns = [
    path('save/', views.SaveTestScore.as_view(), name='save_test_score'),
    path('list/', views.ListOfTestScores.as_view(), name='list_test_scores'),
]