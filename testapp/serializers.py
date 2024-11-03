from rest_framework import serializers
from flashcardapp.models import Flashcard
from reportapp.models import TestResult
from studysetapp.models import StudySet


class TestModeFlashcardSerializer(serializers.ModelSerializer): # under library page of flashcards

    class Meta:
        model = Flashcard
        fields = ['question', 'answer', 'image', 'studyset_instance']
        read_only_fields = ['question', 'answer', 'image', 'studyset_instance']


class TestModeFlashcardSerializerForEmptyReport(serializers.ModelSerializer): # under report page

    studyset_instance = serializers.PrimaryKeyRelatedField(
        queryset=StudySet.objects.all(),
        required=True,
        error_messages={
            'required': 'Please choose a study set',
        }
    )
    class Meta:
        model = Flashcard
        fields = ['question', 'answer', 'image', 'studyset_instance']
        read_only_fields = ['question', 'answer', 'image']