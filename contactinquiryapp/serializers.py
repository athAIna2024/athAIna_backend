from rest_framework import serializers
from .models import ContactInquiry

class ContactInquirySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide your name.',
            'max_length': 'Name must be less than 100 characters.',
            'blank': 'Please provide your name.'
        }
    )

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide your email address.',
            'invalid': 'Please provide a valid email address.',
            'blank': 'Please provide your email address.'
        }
    )

    message = serializers.CharField(
        max_length=300,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a message.',
            'max_length': 'Message must be less than 300 characters.',
            'blank': 'Please provide a message.'
        }
    )

    class Meta:
        model = ContactInquiry
        fields = '__all__'