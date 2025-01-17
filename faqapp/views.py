from rest_framework import generics
from .models import FAQ
from .serializers import FAQSerializer
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from django.http import Http404
# Create your views here.
class CreateFAQ(generics.CreateAPIView):
    serializer_class = FAQSerializer

    def perform_create(self, serializer):
        question = serializer.validated_data.get('question')
        answer = serializer.validated_data.get('answer')
        is_active = serializer.validated_data.get('is_active')
        serializer.save(question=question, answer=answer, is_active=is_active)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'FAQ created successfully.',
                'data': serializer.data,
                'success': True
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'FAQ could not be created, please try again.',
                'errors': serializer.errors,
                'success': False
            }, status=HTTP_400_BAD_REQUEST)

class UpdateAndDeleteFAQ(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all()
    lookup_field = 'id'

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            return Response({
                'message': 'FAQ not found.',
                'success': False
            }, status=HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        question = serializer.validated_data.get('question')
        answer = serializer.validated_data.get('answer')
        is_active = serializer.validated_data.get('is_active')
        serializer.save(question=question, answer=answer, is_active=is_active)

    def update(self, request, *args, **kwargs):
        faq = self.get_object()
        serializer = self.get_serializer(faq, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'message': 'FAQ updated successfully.',
                'data': serializer.data,
                'success': True
            }, status=HTTP_201_CREATED)
        else:
            return Response({
                'message': 'FAQ could not be updated, please try again.',
                'errors': serializer.errors,
                'success': False
            }, status=HTTP_400_BAD_REQUEST)

    def perform_delete(self, serializer):
        serializer.delete()

    def delete(self, request, *args, **kwargs):
        faq = self.get_object()
        serializer = self.get_serializer(faq)

        if serializer:
            self.perform_delete(faq)
            return Response({
                'message': 'FAQ deleted successfully.',
                'data': serializer.data,
                'success': True
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'FAQ could not be deleted, please try again.',
                'success': False
            }, status=HTTP_400_BAD_REQUEST)

class ListOfFAQs(generics.ListAPIView):
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        if not serializer.data:
            return Response({
                'message': 'No FAQs found.',
                'data': serializer.data,
                'success': False
            }, status=HTTP_404_NOT_FOUND)
        else:
            return Response({
                'message': 'FAQs retrieved successfully.',
                'data': serializer.data,
                'success': True
            }, status=HTTP_200_OK)
