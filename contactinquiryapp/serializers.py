from rest_framework import serializers
from .models import ContactInquiry

class ContactInquirySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Your name is needed so we know who to address.',
            'max_length': 'You can use your full name, but it must be less than 100 characters.',
            'blank': 'Your name is needed so we know who to address.'
        }
    )

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Your email address is needed so we can respond to your inquiry.',
            'invalid': 'Please provide a valid email address.',
            'blank': 'Your email address is needed so we can respond to your inquiry.'
        }
    )

    message = serializers.CharField(
        max_length=300,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Your message is needed so we know how to help you.',
            'max_length': 'Message must be less than 300 characters.',
            'blank': 'Your message is needed so we know how to help you.'
        }
    )

    class Meta:
        model = ContactInquiry
        fields = '__all__'