from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from reportapp.serializers import TestResultSerializer
from testapp.models import GeneratedTest
from rest_framework.exceptions import ValidationError


# Create your views here.
class SaveTestResults(generics.CreateAPIView):
    serializer_class = TestResultSerializer

    def extract_studyset_instance(self, batch_id):
        try:
            return GeneratedTest.objects.get(batch_id=batch_id).studyset_instance
        except GeneratedTest.DoesNotExist:
            raise ValidationError('Studyset instance not found.')

    def calculate_score(self, batch_id):
        generated_tests = GeneratedTest.objects.filter(batch_id=batch_id)
        score = generated_tests.filter(correct=True).count()
        return score

    def extract_number_of_questions(self, batch_id):
        generated_tests = GeneratedTest.objects.filter(batch_id=batch_id)
        number_of_questions = generated_tests.count()
        return number_of_questions


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Test results saved successfully.',
                'data': serializer.data,
                'status': HTTP_201_CREATED
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Test results could not be saved, please try again.',
                'errors': serializer.errors,
                'status': HTTP_400_BAD_REQUEST
            }, status=HTTP_400_BAD_REQUEST)

