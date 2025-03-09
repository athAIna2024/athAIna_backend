from django.urls import path
from . import views

urlpatterns = [

    path('', views.ListOfStudySet.as_view(), name='list_studysets'),
    path('save/', views.CreateStudySet.as_view(), name='create_studyset'),
    path('library_studysets/', views.LibraryOfStudySet.as_view(), name='library_StudySet'),
    path('update/<int:id>/', views.UpdateStudySet.as_view(), name='update_StudySet'),

    path('delete/<int:id>/', views.DeleteStudySet.as_view(), name='delete_StudySet'),
]