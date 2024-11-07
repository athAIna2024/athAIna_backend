from rest_framework import serializers
from studysetapp.models import StudySet
from .models import Flashcard
from .validators import validate_image_size

class FlashcardSerializer(serializers.ModelSerializer):
    studyset_instance = serializers.PrimaryKeyRelatedField(
        queryset=StudySet.objects.all(),
        required=True,
        error_messages={
            'required': 'Please choose a study set',
        }
    )

    class Meta:
        model = Flashcard
        fields = ['question', 'answer', 'image', 'studyset_instance', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

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