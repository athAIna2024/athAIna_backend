from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework import generics

from .paginators import SingleQuestionPagination
from .serializers import TestModeFlashcardSerializer
import random
from flashcardapp.models import Flashcard
from studysetapp.models import StudySet
from .validators import validate_number_of_flashcards


class GenerateRandomFlashcards(generics.ListAPIView):
    serializer_class = TestModeFlashcardSerializer
    pagination_class = SingleQuestionPagination

    def get_queryset(self):  # customizing the queryset to be random
        studyset_id = self.request.query_params.get('studyset_id')
        studyset_instance = StudySet.objects.get(id=studyset_id)
        number_of_flashcards = int(self.request.query_params.get('number_of_flashcards'))
        limit = validate_number_of_flashcards(number_of_flashcards, studyset_instance)
        flashcards = list(Flashcard.objects.filter(studyset_instance=studyset_instance))
        random.shuffle(flashcards)
        return flashcards[:limit]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset: # If there is at least one flashcard
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
            else:
                serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'No flashcards found.',
                'data': []
            }, status=HTTP_400_BAD_REQUEST)