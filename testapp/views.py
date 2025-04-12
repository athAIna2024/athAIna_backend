from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
import random
from flashcardapp.models import Flashcard
from flashcardapp.serializers import FlashcardSerializer
from .serializers import GeneratedTestSerializer, TestBatchSerializer
from .tasks import validate_learner_answer_with_ai_task
from django.http import Http404
from rest_framework.exceptions import NotFound
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
                    'successful': False
                }, status=HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError):
            return Response({
                'message': 'Please provide a valid number of questions.',
                'successful': False
            }, status=HTTP_400_BAD_REQUEST)

        random_flashcard_ids = self.randomize_flashcards(number_of_questions)
        if random_flashcard_ids:
            return Response({
                'message': 'Flashcards generated successfully.',
                'flashcard_ids': random_flashcard_ids,
                'successful': True
            }, status=HTTP_201_CREATED)
        return Response({
            'message': 'No flashcards available.',
            'successful': False
        }, status=HTTP_400_BAD_REQUEST)

    def randomize_flashcards(self, number_of_questions):
        queryset = self.get_queryset()
        if queryset.exists():
            random_flashcards = random.sample(list(queryset), number_of_questions)
            return [flashcard.id for flashcard in random_flashcards]
        return []

    def validate_number_of_questions(self, number_of_questions):
        return 0 < number_of_questions <= self.get_queryset().count()


class ValidateLearnerAnswerWithAi(generics.RetrieveAPIView):
    queryset = Flashcard.objects.all()
    serializer_class = FlashcardSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        flashcard_id = self.kwargs.get('id')
        learner_answer = self.request.query_params.get('learner_answer')

        try:
            flashcard = self.get_object()
        except Http404:
            raise NotFound(detail='Flashcard not found with ID {0}'.format(flashcard_id))

        if flashcard:
            correct_answer = flashcard.answer
            question = flashcard.question
            result = validate_learner_answer_with_ai_task.apply_async((question, correct_answer, learner_answer))
            is_correct = result.get()

            return Response({
                'message': 'Validating learner answer with AI.',
                'is_correct': is_correct,
                'successful': True
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Flashcard not found.',
                'successful': False
            }, status=HTTP_400_BAD_REQUEST)


class SaveTestResults(generics.CreateAPIView):
    serializer_class = GeneratedTestSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(self.request.data, list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    'message': 'Test results saved successfully.',
                    'data': serializer.data,
                    'successful': True
                },status=HTTP_201_CREATED)
        except Exception as e:
            return Response({
                    'message': 'An error occurred while saving test results.',
                    'error': str(e),
                    'successful': False
                }, status=HTTP_400_BAD_REQUEST)

class SaveGeneratedTestBatch(generics.CreateAPIView):
    serializer_class = TestBatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Test Batch created successfully.',
                'data': serializer.data,
                'successful': True
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Test Batch could not be created, please try again.',
                'errors': serializer.errors,
                'successful': False
            }, status=HTTP_400_BAD_REQUEST)