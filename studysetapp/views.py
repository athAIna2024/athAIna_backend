from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework import generics
from .models import Document
from .serializers import StudySetSerializer, DocumentSerializer, ChoosePagesFromPDFSerializer
import base64
from .pymupdf_utils import convert_pdf_to_images
from .tasks import convert_pdf_to_images_task

# Create your views here.

class CreateStudySet(generics.CreateAPIView):
    serializer_class = StudySetSerializer

    def perform_create(self, serializer):
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        subjects = serializer.validated_data.get('subjects')
        serializer.save(title=title, description=description, subjects=subjects)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'StudySet created successfully.',
                'data': serializer.data
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'StudySet could not be created, please try again.',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

class UploadDocument(generics.CreateAPIView):
    serializer_class = DocumentSerializer

    def perform_create(self, serializer):
        document = serializer.validated_data.get('document')
        studyset_instance = serializer.validated_data.get('studyset_instance')
        serializer.save(document=document, studyset_instance=studyset_instance)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Document uploaded successfully.',
                'data': serializer.data,
                'status': HTTP_201_CREATED
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Document could not be uploaded, please try again.',
                'status': HTTP_400_BAD_REQUEST,
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

class ChoosePagesFromPDF(generics.UpdateAPIView):
    serializer_class = ChoosePagesFromPDFSerializer
    lookup_field = 'pk'
    queryset = Document.objects.all()

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"detail": "No Document found with ID {0}".format(self.kwargs.get('pk'))})

    def perform_update(self, serializer):
        selected_pages = serializer.validated_data.get('selected_pages')
        serializer.save(selected_pages=selected_pages)

    def partial_update(self, request, *args, **kwargs):
        document = self.get_object()

        # partial=True allows for partial updates
        serializer = self.get_serializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'message': 'Document updated successfully.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Document could not be updated, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

class DisplayPDFImages(generics.RetrieveAPIView):
    lookup_field = 'pk'
    queryset = Document.objects.all()
    serializer_class = ChoosePagesFromPDFSerializer

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"detail": "No Document found with ID {0}".format(self.kwargs.get('pk'))})

    def retrieve(self, request, *args, **kwargs):
        document = self.get_object()
        file_name = document.document.name
        try:
            result = convert_pdf_to_images_task.apply_async(args=(file_name,))
            images = result.get()
            formatted_images = [{"id": idx + 1, "image": img} for idx, img in enumerate(images)]
            return Response({
                'message': 'Document images retrieved successfully.',
                'images': formatted_images,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        except FileNotFoundError:
            raise NotFound({"detail": f"File not found: {file_name}"})
        except RuntimeError as e:
            return Response({
                'message': 'Failed to convert PDF to images.',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

class CheckStatusForPDFToImageConversion(generics.RetrieveAPIView):
    pass

class ExtractTextFromPDF(generics.RetrieveAPIView):
    pass

class GenerateFlashcards(generics.CreateAPIView):
    pass

class CheckStatusForFlashcardGeneration(generics.RetrieveAPIView):
    pass