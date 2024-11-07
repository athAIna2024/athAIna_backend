from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from reportapp.serializers import TestResultSerializer

class SaveTestResults(generics.CreateAPIView):
    serializer_class = TestResultSerializer

    def perform_create(self, serializer):
        studyset_instance = serializer.validated_data.get('studyset_instance')
        score = serializer.validated_data.get('score')
        number_of_questions = serializer.validated_data.get('number_of_questions')
        serializer.save(studyset_instance=studyset_instance, score=score, number_of_questions=number_of_questions)

    def create(self, request, *args, **kwargs):
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