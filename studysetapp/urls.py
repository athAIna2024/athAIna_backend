from django.urls import path
from . import views

urlpatterns = [

    path('create/', views.CreateStudySet.as_view(), name='create_studyset'),
    path('library_studysets/', views.LibraryOfStudySet.as_view(), name='library_StudySet'),
    path('update/<int:id>/', views.UpdateStudySet.as_view(), name='update_StudySet'),

    path('delete/<int:id>/', views.DeleteStudySet.as_view(), name='delete_StudySet'),

    path('search/', views.StudySetSearchView.as_view(), name='studyset-search'),

    path('filter_by_subject/', views.StudySetFilterBySubjectView.as_view(), name='filter_by_subject'),



    path('upload/', views.UploadDocument.as_view(), name='upload_document'),
    path('choose-pages/<int:pk>/', views.ChoosePagesFromPDF.as_view(), name='choose_pages_from_pdf'),
    path('display-pdf-images/', views.DisplayPDFImages.as_view(), name='display_pdf_images'),
    path('extract-text-from-selected-pages/', views.ExtractTextFromPDF.as_view(), name='extract_text_from_selected_pages'),

    path('generate-data-for-flashcards/', views.GenerateDataForFlashcards.as_view(), name='generate_data_for_flashcards'),
    path('generate-flashcards/', views.GenerateFlashcards.as_view(), name='generate_flashcards'),

]