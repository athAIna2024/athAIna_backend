from django.urls import path
from . import views

urlpatterns = [
    path('show-test-result-report/', views.ShowLastSevenTestResults.as_view(), name='show-test-result-report'),
]