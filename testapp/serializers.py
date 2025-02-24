from studysetapp.models import StudySet
from flashcardapp.models import Flashcard
from rest_framework import serializers
from .models import GeneratedTest
import uuid

class GeneratedTestSerializer(serializers.ModelSerializer):
    batch_id = serializers.UUIDField(
        default=uuid.uuid4,
        required=True,
        error_messages={
            "required": "Please provide the test's batch id",
        })

    flashcard_instance = serializers.PrimaryKeyRelatedField(
        queryset=Flashcard.objects.all(),
        required=True,
        error_messages={
            'required': 'Please provide a flashcard instance',
        })

    learner_answer = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        allow_null=True,
        error_messages={
            'max_length': 'Please keep the learner answer under 100 characters.'
        })
    is_correct = serializers.BooleanField(
        default=False,
        required=True,
        error_messages={
            'required': 'Please provide the correctness of the answer',
        })
    created_at = serializers.DateTimeField(
        required=True,
        error_messages={
            'required': 'Please provide the date and time the test was generated.'
        })
    corrected_at = serializers.DateTimeField(
        required=True,
        error_messages={
            'required': 'Please provide the date and time the test was corrected.'
        })

    class Meta:
        model = GeneratedTest
        fields = '__all__'