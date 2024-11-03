# testapp/views.py
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.response import Response
from rest_framework import generics
import random
import uuid
from flashcardapp.models import Flashcard
from .serializers import GenerateRandomFlashcardSerializer, GeneratedTestSerializer

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
                raise ValueError(f"Invalid data: {serializer.errors}")
        return generated_tests