from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from rest_framework import generics

from accountapp.models import Learner
from .models import Document
from .serializers import StudySetSerializer, DocumentSerializer, ChoosePagesFromPDFSerializer, ExtractedDataSerializer, \
    GeneratedDataForFlashcardsSerializer, UpdateStudySetSerializer
from flashcardapp.models import Flashcard
from flashcardapp.serializers import GeneratedFlashcardSerializer
from .tasks import convert_pdf_to_images_task, extract_data_from_pdf_task, generate_flashcards_task, clean_data_for_flashcard_creation_task
import json
from studysetapp.models import StudySet
from studysetapp.paginators import StandardPaginationStudySets
from rest_framework.views import APIView
from django.db.models import Q

from accountapp.models import User
# Create your views here.

class CreateStudySet(generics.CreateAPIView):
    serializer_class = StudySetSerializer

    def perform_create(self, serializer):
        learner_instance = serializer.validated_data.get('learner_instance')
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

class LibraryOfStudySet(generics.ListAPIView):
    serializer_class = StudySetSerializer
    pagination_class = StandardPaginationStudySets

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id') # For authentication, the code will be different
        if user_id:
            try:
                learner = Learner.objects.get(user_id=user_id)  # Assuming Learner model has a user_id field
                return StudySet.objects.filter(learner_instance=learner).order_by('created_at')
            except Learner.DoesNotExist:
                raise Http404("Learner not found")
        return StudySet.objects.none()

    def get(self, request, *args, **kwargs):
        studyset = self.get_queryset()
        page = self.paginate_queryset(studyset)
        serializer = self.get_serializer(page, many=True)

        if not serializer.data:
            return Response({
                'message': 'No Study Sets found.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            response = self.get_paginated_response(serializer.data)
            response.status_code = HTTP_200_OK
            return response
class UpdateStudySet(generics.RetrieveUpdateAPIView):
    queryset = StudySet.objects.all()
    serializer_class = UpdateStudySetSerializer
    lookup_field = 'id'

    # Verify if StudySet learner_instance should be updated or be checked through authentication
    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"detail": "No Study Set found with ID {0}".format(self.kwargs.get('id'))})
    def perform_update(self, serializer):
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        subjects = serializer.validated_data.get('subjects')
        studyset_id = serializer.validated_data.get('studyset_id')
        serializer.save(title=title, description=description, subjects=subjects, studyset_id=studyset_id)

    def put(self, request, *args, **kwargs):
        studyset = self.get_object()

        # partial=True allows for partial updates
        serializer = self.get_serializer(studyset, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'message': 'Study Set updated successfully.',
                'data': serializer.data
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Study Set could not be updated, please try again.',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

class ListOfStudySet(generics.ListAPIView):
    serializer_class = StudySetSerializer
    def get_queryset(self):
        user = self.request.user
        # if user.is_authenticated: ## Uncomment this line (FOR TESTING)
        if user:
            try:
                # learner = Learner.objects.get(user=user)
                learner = Learner.objects.get(user=user)
                return StudySet.objects.filter(learner_instance=learner).order_by('created_at')
            except Learner.DoesNotExist:
                raise Http404("Learner not found")
        return StudySet.objects.none()

    def get(self, request, *args, **kwargs):
        studysets = self.get_queryset()
        serializer = self.get_serializer(studysets, many=True)

        if not serializer.data:
            return Response({
                'message': 'No Study Sets found. Please create one.',
                'data': serializer.data,
                'successful': False,
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Study Sets found.',
                'data': serializer.data,
                'successful': True,
            }, status=HTTP_200_OK)


class StudySetSearchView(APIView):
    def get(self, request, *args, **kwargs):
        title = request.query_params.get('title')
        description = request.query_params.get('description')
        subject = request.query_params.get('subject')
        learner_id = request.query_params.get('learner_id')

        study_sets = StudySet.objects.all()

        if learner_id:
            try:
                learner = Learner.objects.get(id=learner_id)
                study_sets = study_sets.filter(learner_instance=learner)
            except Learner.DoesNotExist:
                return Response({"message": "Learner not found."}, status=HTTP_404_NOT_FOUND)

        query = Q()
        if title:
            query |= Q(title__icontains=title)
        if description:
            query |= Q(description__icontains=description)
        if subject:
            query |= Q(subjects__icontains=subject)

        if query:
            study_sets = study_sets.filter(query)
            serializer = StudySetSerializer(study_sets, many=True)
            return Response(serializer.data)

        return Response({"message": "No query provided."}, status=HTTP_400_BAD_REQUEST)

class StudySetFilterBySubjectView(generics.ListAPIView):
    serializer_class = StudySetSerializer

    def get_queryset(self):
        subject = self.request.query_params.get('q', '')
        if subject:
            return StudySet.objects.filter(subjects=subject).order_by('created_at')
        return StudySet.objects.none()

class DeleteStudySet(generics.RetrieveDestroyAPIView):
    queryset = StudySet.objects.all()
    serializer_class = StudySetSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"detail": "No Study Set found with ID {0}".format(self.kwargs.get('id'))})
    def perform_delete(self, serializer):
        serializer.delete()

    def delete(self, request, *args, **kwargs):
        studyset = self.get_object()
        serializer = self.get_serializer(studyset)

        if serializer:
            self.perform_delete(studyset)
            return Response({
                'message': 'Study set deleted successfully.',
                'data': serializer.data
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Study set could not be deleted, please try again.',
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
    queryset = Document.objects.all()
    serializer_class = ChoosePagesFromPDFSerializer

    def get_object(self):
        pk = self.request.query_params.get('id')
        if not pk:
            raise NotFound({"detail": "No Document ID provided in query parameters."})
        try:
            return self.queryset.get(pk=pk)
        except Document.DoesNotExist:
            raise NotFound({"detail": f"No Document found with ID {pk}"})

    def get(self, request, *args, **kwargs):
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

class ExtractTextFromPDF(generics.GenericAPIView):
    queryset = Document.objects.all()  # Define the queryset

    def get_object(self):
        pk = self.request.query_params.get('id')
        if not pk:
            raise NotFound({"detail": "No Document ID provided in query parameters."})
        try:
            return self.queryset.get(pk=pk)
        except Document.DoesNotExist:
            raise NotFound({"detail": f"No Document found with ID {pk}"})

    def get(self, request, *args, **kwargs):
        document = self.get_object()
        studyset_id = document.studyset_instance.id
        file_name = document.document.name
        selected_pages = document.selected_pages

        if isinstance(selected_pages, str):
            selected_pages = json.loads(selected_pages)
        page_numbers = [int(page) for page in selected_pages]

        try:
            result = extract_data_from_pdf_task.apply_async(args=(file_name, page_numbers))
            text = result.get()
            task_id = result.id
            return Response({
                'message': 'Data extracted successfully.',
                'extracted_text': text,
                'task_id': task_id,
                'studyset_id': studyset_id,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        except FileNotFoundError:
            raise NotFound({"detail": f"File not found: {file_name}"})
        except RuntimeError as e:
            return Response({
                'message': 'Failed to extract data from PDF.',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

class GenerateDataForFlashcards(generics.CreateAPIView):
    serializer_class = ExtractedDataSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'message': 'Invalid data.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

        extracted_data = serializer.validated_data.get('extracted_text')

        try:
            result = generate_flashcards_task.apply_async(args=(extracted_data,))
            data = result.get()
            return Response({
                'message': 'Flashcards generated successfully.',
                'generated_data': data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        except RuntimeError as e:
            return Response({
                'message': 'Failed to generate flashcards.',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

class GenerateFlashcards(generics.GenericAPIView):
    serializer_class = GeneratedDataForFlashcardsSerializer
    queryset = Flashcard.objects.none()  # Set an empty queryset

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'message': 'Invalid data.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

        try:
            valid_flashcards = serializer.validated_data.get('flashcards_data')
            studyset_id = serializer.validated_data.get('studyset_id')

            result = clean_data_for_flashcard_creation_task.apply_async(args=(valid_flashcards, studyset_id))
            validated_data = result.get()
            response_serializer = GeneratedFlashcardSerializer(data=validated_data, many=True)

            if response_serializer.is_valid():
                response_serializer.save()
                return Response({
                    'message': 'Flashcards created successfully.',
                    'data': response_serializer.data,
                    'status': HTTP_200_OK
                }, status=HTTP_200_OK)
            else:
                return Response({
                    'message': 'Failed to serialize generated data.',
                    'errors': response_serializer.errors,
                    'status': HTTP_400_BAD_REQUEST
                }, status=HTTP_400_BAD_REQUEST)

        except RuntimeError as e:
            return Response({
                'message': 'Failed to generate flashcards.',
                'error': str(e),
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)