
from studysetapp.models import StudySet
from rest_framework import serializers
from .models import GeneratedTest
from .validators import validate_flashcard_count
class GeneratedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedTest
        fields = '__all__'
        read_only_fields = ['learner_answer', 'correct']

    def create(self, validated_data):
        batch_id = self.context.get('batch_id')
        if batch_id:
            validated_data['batch_id'] = batch_id
        return GeneratedTest.objects.create(**validated_data)

class LearnerAnswerSerializer(serializers.ModelSerializer):
    question = serializers.CharField(source='flashcard_instance.question', read_only=True)
    answer = serializers.CharField(source='flashcard_instance.answer', read_only=True)

    class Meta:
        model = GeneratedTest
        fields = '__all__'
        read_only_fields = ['studyset_instance', 'flashcard_instance', 'question', 'answer']

    def update(self, instance, validated_data):
        instance.learner_answer = validated_data.get('learner_answer', instance.learner_answer)
        instance.correct = validated_data.get('correct', instance.correct)
        instance.studyset_instance = instance.studyset_instance  # Ensure it's not changed
        instance.flashcard_instance = instance.flashcard_instance  # Ensure it's not changed
        instance.save()
        return instance

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
        validate_flashcard_count(studyset_instance, number_of_flashcards)
        return data

# Create a GeneratedTest for report page 03/11/2024 18:24:00