from rest_framework import serializers
from .models import Flashcard, PDF
from .validators import validate_image_size, validate_studyset_id

class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = ['question', 'answer', 'image', 'studyset_id']

    question = serializers.CharField(
        max_length=300,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a question',
            'blank': 'Please provide a question',
            'max_length': 'Please keep the question under 300 characters.'
        })

    answer = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide an answer',
            'blank': 'Please provide an answer',
            'max_length': 'Please keep the answer under 100 characters.'
        })

    image = serializers.ImageField(
        required=False,
        validators=[validate_image_size],
        error_messages={
            'invalid_image': 'Please provide a valid image file.',
        })

    studyset_id = serializers.IntegerField(
        required=True,
        validators=[validate_studyset_id],
        error_messages={
            'required': 'Please provide a studyset id',
        })