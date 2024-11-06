# testapp/views.py
from django.http import Http404
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from rest_framework import generics, mixins
import random
import uuid
from flashcardapp.models import Flashcard
from .serializers import GenerateRandomFlashcardSerializer, LearnerAnswerSerializer
from rest_framework import generics, mixins
from .models import GeneratedTest
from .serializers import GeneratedTestSerializer
from .paginators import SingleQuestionPagination

class GenerateRandomFlashcards(generics.CreateAPIView):
    serializer_class = GenerateRandomFlashcardSerializer

    def perform_create(self, serializer):
        studyset_instance = serializer.validated_data.get('studyset_instance')
        number_of_flashcards = serializer.validated_data.get('number_of_flashcards')
        flashcards = self.get_random_flashcards(studyset_instance, number_of_flashcards)
        batch_id = str(uuid.uuid4())  # Generate a unique batch ID once
        generated_tests = self.save_generated_tests(studyset_instance, flashcards, batch_id)
        serializer.validated_data['batch_id'] = batch_id
        serializer.validated_data['generated_tests'] = generated_tests

# testapp/views.py
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Generated tests created successfully.',
                'batch_id': serializer.validated_data['batch_id'],
                'generated_tests': GeneratedTestSerializer(serializer.validated_data['generated_tests'], many=True).data,
                'status': HTTP_201_CREATED
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Test mode flashcards could not be generated, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

    def get_random_flashcards(self, studyset_instance, number_of_flashcards):
        flashcards = list(Flashcard.objects.filter(studyset_instance=studyset_instance))
        random.shuffle(flashcards)
        return flashcards[:number_of_flashcards]

    def save_generated_tests(self, studyset_instance, flashcards, batch_id):
        generated_tests = []
        for flashcard in flashcards:
            data = {
                'studyset_instance': studyset_instance.id,
                'flashcard_instance': flashcard.id,
                'batch_id': batch_id  # Use the same batch ID for all tests in this batch
            }
            serializer = GeneratedTestSerializer(data=data, context={'batch_id': batch_id})
            if serializer.is_valid():
                generated_test = serializer.save()
                generated_tests.append(generated_test)
            else:
                return Response({
                    'message': 'Test mode flashcards could not be generated, please try again.',
                    'errors': serializer.errors
                }, status=HTTP_400_BAD_REQUEST)
        return generated_tests

# Pseudocode
# Retrieve all GeneratedTest through batch_id
# Get the first GeneratedTest
# Retrieve the flashcard_instance of the first GeneratedTest
# Before moving to the next GeneratedTest, update the learner_answer and correct fields of the first GeneratedTest
# Get the next GeneratedTest
# Repeat until all GeneratedTest are updated
class NoBackTracking(generics.ListAPIView):
    serializer_class = GeneratedTestSerializer
    pagination_class = SingleQuestionPagination
    queryset = GeneratedTest.objects.all()
    def get_queryset(self):
        batch_id = self.kwargs.get('batch_id')
        return GeneratedTest.objects.filter(batch_id=batch_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        if not serializer.data:
            return Response({
                'message': 'No generated tests found.',
                'data': serializer.data,
                'status': HTTP_404_NOT_FOUND
            }, status=HTTP_404_NOT_FOUND)
        else:
            return Response({
                'message': 'Generated tests retrieved successfully.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)