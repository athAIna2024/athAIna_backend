from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import generics
from .serializers import TestModeFlashcardSerializer
import random
from flashcardapp.models import Flashcard
from studysetapp.models import StudySet

# Create your views here.

class GenerateRandomFlashcards(generics.ListCreateAPIView):
    serializer_class = TestModeFlashcardSerializer

    def get_queryset(self):  # customizing the queryset to be random
        studyset_id = self.request.query_params.get('studyset_id')
        studyset_instance = StudySet.objects.get(id=studyset_id)
        number_of_flashcards = int(self.request.query_params.get('number_of_flashcards'))
        flashcards = list(Flashcard.objects.filter(studyset_instance=studyset_instance))
        random.shuffle(flashcards)
        return flashcards[:number_of_flashcards]

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception as e:
            return Response(str(e), status=HTTP_400_BAD_REQUEST)