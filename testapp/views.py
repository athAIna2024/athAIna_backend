# testapp/views.py
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
import random
import uuid
from flashcardapp.models import Flashcard
from .serializers import GenerateRandomFlashcardSerializer, LearnerAnswerSerializer
from rest_framework import generics
from .models import GeneratedTest
from .serializers import GeneratedTestSerializer
from .paginators import SingleQuestionPagination
from reportapp.serializers import TestResultSerializer
from rest_framework.exceptions import ValidationError
from testapp.ai_learner_answer_validator import validate_learner_answer_with_ai
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
class NoBackTracking(generics.ListAPIView):
    serializer_class = LearnerAnswerSerializer
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
            return self.get_paginated_response(serializer.data)

class LearnerAnswerValidation(generics.RetrieveUpdateAPIView):
    serializer_class = LearnerAnswerSerializer
    queryset = GeneratedTest.objects.all()
    lookup_field = 'flashcard_instance'

    def get_queryset(self):
        batch_id = self.kwargs.get('batch_id')
        return GeneratedTest.objects.filter(batch_id=batch_id)

    def perform_update(self, serializer):
        learner_answer = serializer.validated_data.get('learner_answer')
        answer = serializer.instance.flashcard_instance.answer
        correct = self.validate_learner_answer(learner_answer, answer)
        serializer.save(learner_answer=learner_answer, correct=correct)

    def update(self, request, *args, **kwargs):
        generated_test = self.get_object()
        serializer = self.get_serializer(generated_test, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'message': 'Learner answer validated successfully.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Learner answer could not be validated, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)
    def validate_learner_answer(self, learner_answer, answer):
        # Implement Google-Gemini API to validate partial match answer
        generated_test = self.get_object()
        if learner_answer is not None:
            if learner_answer == answer:
                return True
            else:
                if validate_learner_answer_with_ai(generated_test.flashcard_instance.question, answer, learner_answer):
                    return True
                else:
                    return False

class SaveTestResults(generics.GenericAPIView):
    serializer_class = TestResultSerializer

    def extract_studyset_instance(self, batch_id):
        try:
            return GeneratedTest.objects.filter(batch_id=batch_id).first().studyset_instance
        except GeneratedTest.DoesNotExist:
            raise ValidationError('Studyset instance not found.')

    def calculate_score(self, batch_id):
        generated_tests = GeneratedTest.objects.filter(batch_id=batch_id)
        total_correct = generated_tests.filter(correct=True).count()
        return total_correct

    def extract_number_of_questions(self, batch_id):
        generated_tests = GeneratedTest.objects.filter(batch_id=batch_id)
        total_questions = generated_tests.count()
        return total_questions

    def perform_create(self, serializer, batch_id):
        studyset_instance = self.extract_studyset_instance(batch_id)
        score = self.calculate_score(batch_id)
        total_questions = self.extract_number_of_questions(batch_id)
        serializer.save(studyset_instance=studyset_instance, score=score, number_of_questions=total_questions)

    def get(self, request, *args, **kwargs):
        batch_id = kwargs.get('batch_id')
        score = self.calculate_score(batch_id)
        total_questions = self.extract_number_of_questions(batch_id)
        data = {
            'batch_id': batch_id,
            'score': score,
            'number_of_questions': total_questions
        }
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            self.perform_create(serializer, batch_id)
            feedback = "Well done! Keep it up!" if score >= 70 else "Don't give up! You can do better!"
            return Response({
                'message': 'Test results saved successfully.',
                'total_questions': total_questions,
                'total_correct': score,
                'score': score,
                'feedback': feedback,
                'data': serializer.data,
                'status': HTTP_201_CREATED
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Test results could not be saved, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)