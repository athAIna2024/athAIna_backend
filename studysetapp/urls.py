from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateStudySet.as_view(), name='create_studyset'),

    path('upload/', views.UploadDocument.as_view(), name='upload_document'),
    path('extract-text-from-selected-pages/<int:pk>/', views.ExtractTextFromPDF.as_view(), name='extract_text_from_selected_pages'),
    path('choose-pages/<int:pk>/', views.ChoosePagesFromPDF.as_view(), name='choose_pages_from_pdf'),
    path('display-pdf-images/<int:pk>/', views.DisplayPDFImages.as_view(), name='display_pdf_images'),
]