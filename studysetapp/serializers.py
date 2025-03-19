from rest_framework import serializers

from accountapp.models import Learner
from .models import StudySet, Document
from .validators import validate_file_extension

class StudySetSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySet
        fields = ['id', 'learner_instance', 'title', 'description', 'subject', 'created_at', 'updated_at']

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
        fields = ['id', 'learner_instance', 'title', 'description', 'subject', 'updated_at']

    id = serializers.IntegerField(read_only=True)
    learner_instance = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

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
        required=False,
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
