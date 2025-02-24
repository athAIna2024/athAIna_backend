from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
import random
from flashcardapp.models import Flashcard
from flashcardapp.serializers import FlashcardSerializer

class GenerateRandomFlashcards(generics.RetrieveAPIView):
    serializer_class = FlashcardSerializer

    def get_queryset(self):
        studyset_id = self.request.query_params.get('studyset_id')
        if studyset_id:
            return Flashcard.objects.filter(studyset_instance=studyset_id)
        return Flashcard.objects.none()

    def get(self, request, *args, **kwargs):
        number_of_questions = self.request.query_params.get('number_of_questions')
        try:
            number_of_questions = int(number_of_questions)
            if not self.validate_number_of_questions(number_of_questions):
                return Response({
                    'message': 'The number of questions exceeds the available flashcards.',
                    'status': HTTP_400_BAD_REQUEST
                }, status=HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({
                'message': 'Please provide a valid number of questions.',
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

        random_flashcard_ids = self.randomize_flashcards(number_of_questions)
        if random_flashcard_ids:
            return Response({
                'message': 'Flashcards generated successfully.',
                'flashcard_ids': random_flashcard_ids,
                'status': HTTP_201_CREATED
            }, status=HTTP_201_CREATED)
        return Response({
            'message': 'No flashcards available.',
            'status': HTTP_400_BAD_REQUEST
        }, status=HTTP_400_BAD_REQUEST)

    def randomize_flashcards(self, number_of_questions):
        queryset = self.get_queryset()
        if queryset.exists():
            random_flashcards = random.sample(list(queryset), number_of_questions)
            return [flashcard.id for flashcard in random_flashcards]
        return []

    def validate_number_of_questions(self, number_of_questions):
        return 0 < number_of_questions <= self.get_queryset().count()