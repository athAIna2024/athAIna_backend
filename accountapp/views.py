from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework import status
from accountapp.serializers import UserRegistrationSerializer
from accountapp.utils import send_code_to_user
from rest_framework.response import Response


# Create your views here.

class RegisterView(GenericAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            send_code_to_user(user_data['email'])
            return Response({
                "data": user,
                "message": "User created successfully",
            },status=status.HTTP_201_CREATED)
        return Response({serializer.errors},status=status.HTTP_400_BAD_REQUEST)
