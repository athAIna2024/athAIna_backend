from rest_framework import serializers

from accountapp.models import Learner
from .models import StudySet, Document
from .validators import validate_file_extension

class StudySetSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySet
        fields = ['id', 'learner_instance', 'title', 'description', 'subject', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    id = serializers.IntegerField(read_only=True)

    learner_instance = serializers.PrimaryKeyRelatedField(
        queryset=Learner.objects.all(),
        required=True,
        error_messages={
            'required': 'Please provide a learner instance',
        })

    title = serializers.CharField(
        max_length=60,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a title',
            'blank': 'Please provide a title',
            'max_length': 'Please keep the title under 60 characters.'
        })

    description = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a description',
            'blank': 'Please provide a description',
            'max_length': 'Please keep the description under 100 characters.'
        })

    subject = serializers.ChoiceField(
        choices=StudySet.SubjectChoices.choices,
        required=True,
        error_messages={
            'required': 'Please provide a subject',
        })

class UpdateStudySetSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySet
        fields = ['title', 'description', 'subject']

    title = serializers.CharField(
        max_length=60,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a title',
            'blank': 'Please provide a title',
            'max_length': 'Please keep the title under 60 characters.'
        })

    description = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a description',
            'blank': 'Please provide a description',
            'max_length': 'Please keep the description under 100 characters.'
        })

    subject = serializers.ChoiceField(
        choices=StudySet.SubjectChoices.choices,
        required=True,
        error_messages={
            'required': 'Please provide a subject',
        })


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['document', 'studyset_instance']
        read_only_fields = ['selected_pages', 'uploaded_at']

    document = serializers.FileField(
        required=True,
        validators=[validate_file_extension],
        error_messages={
            'required': 'Please provide a document',
        })

    studyset_instance = serializers.PrimaryKeyRelatedField(
        queryset=StudySet.objects.all(),
        required=True,
        error_messages={
            'required': 'Please provide a study set instance',
        })

class ChoosePagesFromPDFSerializer(serializers.Serializer):
    selected_pages = serializers.JSONField(
        required=True,
        error_messages={
            'required': 'Please provide the selected pages',
        })

    class Meta:
        model = Document
        fields = ['selected_pages']
        read_only_fields = ['document', 'studyset_instance', 'uploaded_at']

    # Override since we are not using another serializer for saving the selected pages
    # to the Document model
    # For Flashcard Serializer both create and update modifies all model fields
    def update(self, instance, validated_data):
        instance.selected_pages = validated_data.get('selected_pages', instance.selected_pages)
        instance.save()
        return instance

class ExtractedDataSerializer(serializers.Serializer):
    extracted_text = serializers.CharField(
        required=True,
        error_messages={
            'required': 'Please provide the extracted text',
        })

class GeneratedDataForFlashcardsSerializer(serializers.Serializer):
    flashcards_data = serializers.ListField(
        child=serializers.JSONField(),
        required=True,
        error_messages={
            'required': 'Please provide the flashcards data',
        })
    studyset_id = serializers.IntegerField(
        required=True,
        error_messages={
            'required': 'Please provide the study set ID',
        })