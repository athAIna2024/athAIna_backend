from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import generics

from studysetapp.models import StudySet
from .models import Flashcard
from .paginators import StandardPaginationFlashcards, ReviewModePaginationFlashcard
from .serializers import FlashcardSerializer
from rest_framework.views import APIView
from django.db.models import Q

from accountapp.models import User
from accountapp.models import Learner
class CreateFlashcard(generics.CreateAPIView):
    serializer_class = FlashcardSerializer

    def perform_create(self, serializer):
        question = serializer.validated_data.get('question')
        answer = serializer.validated_data.get('answer')
        image = serializer.validated_data.get('image')
        studyset_instance = serializer.validated_data.get('studyset_instance')
        serializer.save(question=question, answer=answer, image=image, studyset_instance=studyset_instance)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Flashcard created successfully.',
                'data': serializer.data,
                'successful': True,
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Flashcard could not be created, please try again.',
                'errors': serializer.errors,
                'successful': False,
            }, status=HTTP_400_BAD_REQUEST)

class ListOfFlashcards(generics.ListAPIView):
    serializer_class = FlashcardSerializer

    def get_queryset(self):
        studyset_id = self.request.query_params.get('studyset_id')
        if studyset_id:
            try:
                studyset_instance = StudySet.objects.get(id=studyset_id)
                return Flashcard.objects.filter(studyset_instance=studyset_instance).order_by('updated_at')
            except StudySet.DoesNotExist:
                raise NotFound({"message": "No StudySet found with ID {0}".format(studyset_id)})
        return Flashcard.objects.none()

    def get(self, request, *args, **kwargs):
        flashcards = self.get_queryset()
        serializer = self.get_serializer(flashcards, many=True)

        if not serializer.data:
            return Response({
                'message': 'No flashcards found. Please create some flashcards.',
                'data': serializer.data,
                'successful': False,
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Flashcards retrieved successfully.',
                'data': serializer.data,
                'successful': True,
            }, status=HTTP_200_OK)


class LibraryOfFlashcards(generics.ListAPIView):
    serializer_class = FlashcardSerializer
    pagination_class = StandardPaginationFlashcards

    def get_queryset(self):
        studyset_id = self.request.query_params.get('studyset_id')
        if studyset_id:
            try:
                studyset_instance = StudySet.objects.get(id=studyset_id)
                return Flashcard.objects.filter(studyset_instance=studyset_instance).order_by('created_at')
            except StudySet.DoesNotExist:
                raise Http404("StudySet not found")
        return Flashcard.objects.none()

    def get(self, request, *args, **kwargs):
        flashcards = self.get_queryset()
        page = self.paginate_queryset(flashcards)
        serializer = self.get_serializer(page, many=True)

        if not serializer.data:
            return Response({
                'message': 'No flashcards found.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            response = self.get_paginated_response(serializer.data)
            response.status_code = HTTP_200_OK
            return response


class ReviewModeFlashcard(generics.ListAPIView):
    serializer_class = FlashcardSerializer
    pagination_class = ReviewModePaginationFlashcard

    def get_queryset(self):
        studyset_id = self.request.query_params.get('studyset_id')
        if studyset_id:
            try:
                studyset_instance = StudySet.objects.get(id=studyset_id)
                return Flashcard.objects.filter(studyset_instance=studyset_instance).order_by('created_at')
            except StudySet.DoesNotExist:
                raise Http404("StudySet not found")
        return Flashcard.objects.none()

    def get(self, request, *args, **kwargs):
        flashcards = self.get_queryset()
        page = self.paginate_queryset(flashcards)
        serializer = self.get_serializer(page, many=True)

        if not serializer.data:
            return Response({
                'message': 'No flashcards found.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            response = self.get_paginated_response(serializer.data)
            response.status_code = HTTP_200_OK
            return response

class UpdateFlashcard(generics.RetrieveUpdateAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"message": "No Flashcard found with ID {0}".format(self.kwargs.get('id'))})

    def perform_update(self, serializer):
        question = serializer.validated_data.get('question')
        answer = serializer.validated_data.get('answer')
        if 'image' in serializer.validated_data: # If image is being updated
            image = serializer.validated_data.get('image')
        else:
            image = self.get_object().image
        studyset_instance = serializer.validated_data.get('studyset_instance')
        serializer.save(question=question, answer=answer, image=image, studyset_instance=studyset_instance)

    def update(self, request, *args, **kwargs):
        flashcard = self.get_object()

        # partial=True allows for partial updates
        serializer = self.get_serializer(flashcard, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'message': 'Flashcard updated successfully.',
                'data': serializer.data,
                'successful': True,
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Flashcard could not be updated, please try again.',
                'errors': serializer.errors,
                'successful': False,
            }, status=HTTP_400_BAD_REQUEST)

class DeleteFlashcard(generics.RetrieveDestroyAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"detail": "No Flashcard found with ID {0}".format(self.kwargs.get('id'))})
    def perform_delete(self, serializer):
        serializer.delete()

    def delete(self, request, *args, **kwargs):
        flashcard = self.get_object()
        serializer = self.get_serializer(flashcard)

        if serializer:
            self.perform_delete(flashcard)
            return Response({
                'message': 'Flashcard deleted successfully.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Flashcard could not be deleted, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

class FlashcardSearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')  # Get the search query
        studyset_id = request.query_params.get('studyset_id')  # Get the studyset ID

        if query:
            flashcards = Flashcard.objects.all()
            if studyset_id:
                try:
                    studyset_instance = StudySet.objects.get(id=studyset_id)
                    flashcards = flashcards.filter(studyset_instance=studyset_instance)
                except StudySet.DoesNotExist:
                    raise Http404("StudySet not found")

            flashcards = flashcards.filter(
                Q(question__icontains=query) | Q(answer__icontains=query)
            )
            serializer = FlashcardSerializer(flashcards, many=True)
            return Response(serializer.data)

        return Response({"message": "No query provided."}, status=HTTP_400_BAD_REQUEST)