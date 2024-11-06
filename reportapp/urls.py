from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:batch_id>/save_test_results/', views.SaveTestResults.as_view(), name='test-results'),
]