from rest_framework import serializers
from .models import FAQ

class FAQSerializer(serializers.ModelSerializer):
    question = serializers.CharField(
        max_length=300,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a question',
            'blank': 'Please provide a question',
            'max_length': 'Please keep the question under 300 characters.'
        }
    )

    answer = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide an answer',
            'blank': 'Please provide an answer',
        }
    )

    is_active = serializers.BooleanField(
        required=False
    )

    class Meta:
        model = FAQ
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']