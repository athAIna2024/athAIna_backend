from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework import generics

from .models import Document
from .serializers import StudySetSerializer, DocumentSerializer, ChoosePagesFromPDFSerializer
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

class ChoosePagesFromPDF(generics.RetrieveUpdateAPIView):
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

    def update(self, request, *args, **kwargs):
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



class ExtractTextFromPDF(generics.GenericAPIView):
    pass

class GenerateFlashcards(generics.CreateAPIView):
    pass