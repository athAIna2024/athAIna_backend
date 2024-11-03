from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework import generics
import random
from flashcardapp.models import Flashcard
from studysetapp.models import StudySet
from .serializers import GenerateRandomFlashcardSerializer, TestModeFlashcardSerializer
from .validators import validate_number_of_flashcards
from .paginators import SingleQuestionPagination

class GenerateRandomFlashcards(generics.GenericAPIView): # We did not use ListAPIView because this is customized to return a single question
    serializer_class = GenerateRandomFlashcardSerializer
    pagination_class = SingleQuestionPagination

    def get_queryset(self):
        return Flashcard.objects.none()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            studyset_instance = serializer.validated_data.get('studyset_instance')
            number_of_flashcards = serializer.validated_data.get('number_of_flashcards')
            flashcards = self.get_random_flashcards(studyset_instance, number_of_flashcards)
            return self.create_response(flashcards)
        else:
            return Response({
                'message': 'Test mode flashcards could not be generated, please try again.',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

    def get_random_flashcards(self, studyset_instance, number_of_flashcards):
        limit = validate_number_of_flashcards(number_of_flashcards, studyset_instance)
        flashcards = list(Flashcard.objects.filter(studyset_instance=studyset_instance))
        random.shuffle(flashcards)
        return flashcards[:limit]

    def create_response(self, flashcards):
        serializer = TestModeFlashcardSerializer
        if flashcards:  # If there is at least one flashcard
            page = self.paginate_queryset(flashcards)
            if page is not None:
                paginated_serializer = self.get_paginated_response(serializer(page, many=True).data)
            else:
                paginated_serializer = serializer(flashcards, many=True)
            return Response(paginated_serializer.data, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'No flashcards found.',
            }, status=HTTP_400_BAD_REQUEST)