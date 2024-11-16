from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from django.http import Http404
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q


from .models import StudySet
from .serializers import StudySetSerializer
from .paginators import StandardPaginationStudySets

class CreateStudySet(generics.CreateAPIView):
    serializer_class = StudySetSerializer

    def perform_create(self, serializer):
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        subjects = serializer.validated_data.get('subjects')
        serializer.save(title=title, description=description, subjects=subjects)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'StudySet created successfully.',
                'data': serializer.data
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'StudySet could not be created, please try again.',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)

class LibraryOfStudySet(generics.ListAPIView):
    queryset = StudySet.objects.all().order_by('created_at')
    serializer_class = StudySetSerializer
    pagination_class = StandardPaginationStudySets

    try:
        queryset = StudySet.objects.all()
    except StudySet.DoesNotExist:
        raise Http404("No Study Sets found")

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
    serializer_class = StudySetSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise NotFound({"detail": "No Study Set found with ID {0}".format(self.kwargs.get('id'))})
    def perform_update(self, serializer):
        title = serializer.validated_data.get('title')
        description = serializer.validated_data.get('description')
        subjects = serializer.validated_data.get('subjects')
        studyset_id = serializer.validated_data.get('studyset_id')
        serializer.save(title=title, description=description, subjects=subjects, studyset_id=studyset_id)

    def put(self, request, *args, **kwargs):
        studyset = self.get_object()

        # partial=True allows for partial updates
        serializer = self.get_serializer(studyset, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'message': 'Study Set updated successfully.',
                'data': serializer.data
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Study Set could not be updated, please try again.',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)


class StudySetSearchView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')

        if query:
            study_sets = StudySet.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
            serializer = StudySetSerializer(study_sets, many=True)
            return Response(serializer.data)

        return Response({"message": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)


class StudySetFilterBySubjectView(generics.ListAPIView):
    serializer_class = StudySetSerializer

    def get_queryset(self):
        subject = self.request.query_params.get('q', '')
        if subject:
            return StudySet.objects.filter(subjects=subject).order_by('created_at')
        return StudySet.objects.none()



# class DeleteStudySet(generics.RetrieveDestroyAPIView):
#     queryset = StudySet.objects.all()
#     serializer_class = StudySetSerializer
#     lookup_field = 'id'
#
#     def get_object(self):
#         try:
#             return super().get_object()
#         except Http404:
#             raise NotFound({"detail": "No Study Set found with ID {0}".format(self.kwargs.get('id'))})
#     def perform_delete(self, serializer):
#         serializer.delete()
#
#     def delete(self, request, *args, **kwargs):
#         studyset = self.get_object()
#         serializer = self.get_serializer(studyset)
#
#         if serializer:
#             self.perform_delete(studyset)
#             return Response({
#                 'message': 'Study set deleted successfully.',
#                 'data': serializer.data
#             }, status=HTTP_200_OK)
#         else:
#             return Response({
#                 'message': 'Study set could not be deleted, please try again.',
#                 'errors': serializer.errors
#             }, status=HTTP_400_BAD_REQUEST)
