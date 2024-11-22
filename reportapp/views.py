from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK

from reportapp.models import TestResult
from reportapp.serializers import TestResultSerializer
from studysetapp.models import StudySet


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

class ShowLastSevenTestResults(generics.ListAPIView):
    serializer_class = TestResultSerializer
    queryset = TestResult.objects.all()

    def get_queryset(self):
        studyset_id = self.request.query_params.get('studyset_id')
        studyset_instance = StudySet.objects.get(id=studyset_id)
        if studyset_id:
            return TestResult.objects.filter(studyset_instance=studyset_id).order_by('-submitted_at')[:7]
        return TestResult.objects.none()

    def get(self, request, *args, **kwargs):
        test_results = self.get_queryset()
        serializer = self.get_serializer(test_results, many=True)
        return Response({
            'message': 'Last seven test results.',
            'data': serializer.data,
            'status': HTTP_200_OK
        }, status=HTTP_200_OK)