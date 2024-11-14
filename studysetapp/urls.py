from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateStudySet.as_view(), name='create_studyset'),
    path('upload/', views.UploadDocument.as_view(), name='upload_document'),
]