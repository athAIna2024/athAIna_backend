# testapp/views.py
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from rest_framework import generics
import random
import uuid
from flashcardapp.models import Flashcard
from .serializers import GenerateRandomFlashcardSerializer, LearnerAnswerSerializer
from rest_framework import generics, mixins
from .models import GeneratedTest
from .serializers import GeneratedTestSerializer
from .paginators import SingleQuestionPagination

class GenerateRandomFlashcards(generics.GenericAPIView):
    serializer_class = GenerateRandomFlashcardSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            studyset_instance = serializer.validated_data.get('studyset_instance')
            number_of_flashcards = serializer.validated_data.get('number_of_flashcards')
            flashcards = self.get_random_flashcards(studyset_instance, number_of_flashcards)
            batch_id = str(uuid.uuid4())  # Generate a unique batch ID once
            generated_tests = self.save_generated_tests(studyset_instance, flashcards, batch_id)
            return Response({
                'message': 'Generated tests created successfully.',
                'batch_id': batch_id,
                'generated_tests': GeneratedTestSerializer(generated_tests, many=True).data
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Test mode flashcards could not be generated, please try again.',
                'errors': serializer.errors
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

class PresentFlashCardView(generics.GenericAPIView):
    serializer_class = LearnerAnswerSerializer
    pagination_class = SingleQuestionPagination

    def get_queryset(self):
        generated_tests = GeneratedTest.objects.filter(batch_id=self.kwargs.get('batch_id'))
        return generated_tests

    def get(self, request, *args, **kwargs):
        generated_tests = self.get_queryset()
        page = self.paginate_queryset(generated_tests)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(generated_tests, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def validate_learner_answer(self, flashcard_id, studyset_instance, learner_answer):
        flashcard = Flashcard.objects.get(id=flashcard_id, studyset_instance=studyset_instance)
        return flashcard.answer in learner_answer
    def put(self, request, *args, **kwargs):
        pass

