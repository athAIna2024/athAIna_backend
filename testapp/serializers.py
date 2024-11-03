from rest_framework import serializers
from flashcardapp.models import Flashcard
from studysetapp.models import StudySet
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import GeneratedTest

class GeneratedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTest
        fields = '__all__'

    learner_answer = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=100,
        error_messages={
            'max_length': 'Please keep your answer under 100 characters.',
        }
    )

    def create(self, validated_data):
        batch_id = self.context.get('batch_id')
        if batch_id:
            validated_data['batch_id'] = batch_id
        return GeneratedTest.objects.create(**validated_data)
class GenerateRandomFlashcardSerializer(serializers.Serializer):

    studyset_instance = serializers.PrimaryKeyRelatedField(
        queryset=StudySet.objects.all(),
        required=True,
        error_messages={
            'required': 'Please choose a study set',
        }
    )

    number_of_flashcards = serializers.IntegerField(
        required=True,
        error_messages={
            'required': 'Please enter the number of flashcards',
        }
    )

    def validate(self, data):
        studyset_instance = data.get('studyset_instance')
        number_of_flashcards = data.get('number_of_flashcards')
        total_flashcards = Flashcard.objects.filter(studyset_instance=studyset_instance).count()
        if number_of_flashcards > total_flashcards or number_of_flashcards < 1:
            raise ValidationError(f'The study set only has {total_flashcards} flashcards.')
        return data

# Create a GeneratedTest for report page 03/11/2024 18:24:00