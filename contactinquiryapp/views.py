
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework import generics
from .models import ContactInquiry
from .serializers import ContactInquirySerializer

class ContactInquiryCreate(generics.CreateAPIView):
    queryset = ContactInquiry.objects.all()
    serializer_class = ContactInquirySerializer

    def perform_create(self, serializer):
        name = serializer.validated_data.get('name')
        email = serializer.validated_data.get('email')
        message = serializer.validated_data.get('message')
        serializer.save(name=name, email=email, message=message)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'message': 'Your contact inquiry has been submitted.',
                'data': serializer.data
            }, status=HTTP_200_OK)
        else:
            return Response({
                'message': 'Your contact inquiry could not be submitted, please try again.',
                'errors': serializer.errors
            }, status=HTTP_400_BAD_REQUEST)
