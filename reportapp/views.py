from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from .serializers import TestReportSerializer, TestReportSerializerReadOnly
from .models import TestReport
from accountapp.models import Learner, User
from studysetapp.models import StudySet
from rest_framework.exceptions import NotFound
from django.http import Http404

class SaveTestScore(generics.CreateAPIView):
    serializer_class = TestReportSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Test score saved successfully.',
                'data': serializer.data,
                'successful': True
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Test score could not be saved, please try again.',
                'errors': serializer.errors,
                'successful': False
            }, status=HTTP_400_BAD_REQUEST)


class ListOfTestScores(generics.ListAPIView):
    serializer_class = TestReportSerializerReadOnly

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')

        if user_id:
            try:
                user = User.objects.get(id=user_id)
                learner = Learner.objects.get(user=user)
                studysets = StudySet.objects.filter(learner_instance=learner)
                test_scores = TestReport.objects.filter(studyset_instance__in=studysets)
                return test_scores
            except Learner.DoesNotExist:
                raise NotFound({"message": "No learner found with user ID {0}".format(user_id)})
            except User.DoesNotExist:
                raise NotFound({"message": "No user found with ID {0}".format(user_id)})
        return TestReport.objects.none()

    def get(self, request, *args, **kwargs):
        test_scores = self.get_queryset()
        serializer = self.get_serializer(test_scores, many=True)

        if not serializer.data:
            return Response({
                'message': 'No test scores found.',
                'successful': False
            }, status=HTTP_400_BAD_REQUEST)
        return Response({
            'message': 'Test scores found.',
            'data': serializer.data,
            'successful': True
        }, status=HTTP_200_OK)
