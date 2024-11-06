from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import generics
from .models import Flashcard, PDF
from .paginators import StandardPaginationFlashcards, ReviewModePaginationFlashcard
from .serializers import FlashcardSerializer

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
                'status': HTTP_201_CREATED
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Flashcard could not be created, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

class ListOfFlashcards(generics.ListAPIView):
    queryset = Flashcard.objects.all().order_by('created_at')
    serializer_class = FlashcardSerializer

    try:
        queryset = Flashcard.objects.all()
    except Flashcard.DoesNotExist:
        raise Http404("No Flashcards found")

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
            return self.get_paginated_response(serializer.data)
class LibraryOfFlashcards(generics.ListAPIView):
    queryset = Flashcard.objects.all().order_by('created_at')
    serializer_class = FlashcardSerializer
    pagination_class = StandardPaginationFlashcards

    try:
        queryset = Flashcard.objects.all()
    except Flashcard.DoesNotExist:
        raise Http404("No Flashcards found")

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
    queryset = Flashcard.objects.all().order_by('created_at')
    serializer_class = FlashcardSerializer
    pagination_class = ReviewModePaginationFlashcard

    try:
        queryset = Flashcard.objects.all()
    except Flashcard.DoesNotExist:
        raise Http404("No Flashcards found")

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
            raise NotFound({"detail": "No Flashcard found with ID {0}".format(self.kwargs.get('id'))})

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
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Flashcard could not be updated, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
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

