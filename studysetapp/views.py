from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework import generics
from .models import StudySet
from .serializers import StudySetSerializer, DocumentSerializer
from flashcardapp.serializers import GeneratedFlashcardSerializer
from .generate_flashcards_with_ai import generate_data_for_flashcards, populate_flashcards
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

class ChoosePagesFromPDF(generics.GenericAPIView):
    pass

class ExtractTextFromPDF(generics.GenericAPIView):
    pass

class GenerateFlashcards(generics.CreateAPIView):
    pass