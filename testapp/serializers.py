from flashcardapp.models import Flashcard
from rest_framework import serializers
from .models import GeneratedTest

class BulkCreateGeneratedTestSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        instances = [self.child.Meta.model(**item) for item in validated_data]
        try:
            return self.child.Meta.model.objects.bulk_create(instances)
        except Exception as e:
            raise serializers.ValidationError(f"Bulk create failed: {str(e)}")

class GeneratedTestSerializer(serializers.ModelSerializer):
    batch_id = serializers.UUIDField(
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
        list_serializer_class = BulkCreateGeneratedTestSerializer
        fields = ['batch_id', 'flashcard_instance', 'learner_answer', 'is_correct', 'created_at', 'corrected_at']
        read_only_fields = ['deleted_at', 'restored_at', 'transaction_id']



