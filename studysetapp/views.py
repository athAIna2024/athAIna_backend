from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from rest_framework.response import Response
from rest_framework import generics
from accountapp.models import Learner
from .serializers import StudySetSerializer, UpdateStudySetSerializer
from studysetapp.models import StudySet
from studysetapp.paginators import StandardPaginationStudySets

from accountapp.models import User
# Create your views here.

class CreateStudySet(generics.CreateAPIView):
    serializer_class = StudySetSerializer

    def perform_create(self, serializer):
        learner_instance = serializer.validated_data.get('learner_instance')
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        subject = serializer.validated_data.get('subject')
        serializer.save(learner_instance=learner_instance, title=title, description=description, subject=subject)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Study Set created successfully.',
                'data': serializer.data,
                'successful': True
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Study Set could not be created, please try again.',
                'errors': serializer.errors,
                'successful': False
            }, status=HTTP_400_BAD_REQUEST)

class LibraryOfStudySet(generics.ListAPIView):
    serializer_class = StudySetSerializer
    pagination_class = StandardPaginationStudySets

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id') # For authentication, the code will be different
        if user_id:
            try:
                learner = Learner.objects.get(user_id=user_id)  # Assuming Learner model has a user_id field
                return StudySet.objects.filter(learner_instance=learner).order_by('created_at')
            except Learner.DoesNotExist:
                raise Http404("Learner not found")
        return StudySet.objects.none()

    def get(self, request, *args, **kwargs):
        studyset = self.get_queryset()
        page = self.paginate_queryset(studyset)
        serializer = self.get_serializer(page, many=True)

        if not serializer.data:
            return Response({
                'message': 'No Study Sets found.',
                'data': serializer.data,
                'status': HTTP_200_OK
            }, status=HTTP_200_OK)
        else:
            response = self.get_paginated_response(serializer.data)
            response.status_code = HTTP_200_OK
            return response
class UpdateStudySet(generics.RetrieveUpdateAPIView):
    queryset = StudySet.objects.all()
    serializer_class = UpdateStudySetSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"message": "No Study Set found with ID {0}".format(self.kwargs.get('id'))})

    def perform_update(self, serializer):
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        subject = serializer.validated_data.get('subject')
        serializer.save(title=title, description=description, subject=subject)

    def put(self, request, *args, **kwargs):
        studyset = self.get_object()

        # partial=True allows for partial updates
        serializer = self.get_serializer(studyset, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'message': 'Study Set updated successfully.',
                'data': serializer.data,
                'successful': True
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Study Set could not be updated, please try again.',
                'errors': serializer.errors,
                'successful': False
            }, status=HTTP_400_BAD_REQUEST)

class ListOfStudySet(generics.ListAPIView):
    serializer_class = StudySetSerializer
    def get_queryset(self):
        user_id = self.request.query_params.get('user_id') # For authentication, the code will be different
        if user_id:
            user = User.objects.get(id=user_id)
        # if user.is_authenticated: ## Uncomment this line (FOR TESTING),
            if user:
                try:
                    learner = Learner.objects.get(user=user)
                    return StudySet.objects.filter(learner_instance=learner).order_by('-updated_at')
                except Http404:
                    raise NotFound({"message": "No Study Set found with ID {0}".format(self.kwargs.get('id'))})
        return StudySet.objects.none()

    def get(self, request, *args, **kwargs):
        studysets = self.get_queryset()
        serializer = self.get_serializer(studysets, many=True)

        if not serializer.data:
            return Response({
                'message': 'No Study Sets found. Please create one.',
                'data': serializer.data,
                'successful': False,
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Study Sets found.',
                'data': serializer.data,
                'successful': True,
            }, status=HTTP_200_OK)

class DeleteStudySet(generics.RetrieveDestroyAPIView):
    queryset = StudySet.objects.all()
    serializer_class = StudySetSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"message": "No Study Set found with ID {0}".format(self.kwargs.get('id'))})
    def perform_delete(self, serializer):
        serializer.delete()

    def delete(self, request, *args, **kwargs):
        studyset = self.get_object()
        serializer = self.get_serializer(studyset)

        if serializer:
            self.perform_delete(studyset)
            return Response({
                'message': 'Study set deleted successfully.',
                'successful': True,
                'data': serializer.data
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Study set could not be deleted, please try again.',
                'successful': False,
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

