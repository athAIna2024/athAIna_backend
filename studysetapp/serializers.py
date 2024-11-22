from rest_framework import serializers
from .models import StudySet

class StudySetSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySet
        fields = ['title', 'description', 'subjects']

    title = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a title',
            'blank': 'Please provide a title',
            'max_length': 'Please keep the title under 60 characters.'
        })

    description = serializers.CharField(
        max_length=300,
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'Please provide a description',
            'blank': 'Please provide a description',
            'max_length': 'Please keep the description under 100 characters.'
        })

    subjects = serializers.ChoiceField(
        choices=StudySet.SubjectChoices.choices,
        required=True,
        error_messages={
            'required': 'Please provide a subject',
        })

