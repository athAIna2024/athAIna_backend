from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateStudySet.as_view(), name='create_studyset'),

    path('upload/', views.UploadDocument.as_view(), name='upload_document'),
    path('choose-pages/<int:pk>/', views.ChoosePagesFromPDF.as_view(), name='choose_pages_from_pdf'),
    path('display-pdf-images/', views.DisplayPDFImages.as_view(), name='display_pdf_images'),
    path('extract-text-from-selected-pages/', views.ExtractTextFromPDF.as_view(), name='extract_text_from_selected_pages'),

    path('generate-data-for-flashcards/', views.GenerateDataForFlashcards.as_view(), name='generate_data_for_flashcards'),
    # path('generate-flashcards/', views.GenerateFlashcards.as_view(), name='generate_flashcards'),

]