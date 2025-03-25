from rest_framework import serializers
from .models import TestReport
from studysetapp.models import StudySet
from testapp.models import TestBatch

class TestReportSerializer(serializers.ModelSerializer):
    studyset_instance = serializers.PrimaryKeyRelatedField(
        queryset=StudySet.objects.all(),
        required=True,
        error_messages={
            'required': 'Please choose a study set',
        }
    )

    batch = serializers.PrimaryKeyRelatedField(
        queryset=TestBatch.objects.all(),
        required=True,
        error_messages={
            'required': 'Please choose a test batch',
        }
    )

    score = serializers.IntegerField(
        required=True,
        error_messages={
            'required': 'Please provide a score',
        }
    )

    number_of_questions = serializers.IntegerField(
        required=True,
        error_messages={
            'required': 'Please provide the number of questions',
        }
    )

    submitted_at = serializers.DateTimeField(
        required=True,
        error_messages={
            'required': 'Please provide the date and time the test was submitted',
        }
    )

    class Meta:
        model = TestReport
        fields = '__all__'
        read_only_fields = ['id']

class TestReportSerializerReadOnly(serializers.ModelSerializer):

    class Meta:
        model = TestReport
        fields = '__all__'
        read_only_fields = ['id', 'studyset_instance', 'batch', 'score', 'number_of_questions', 'submitted_at']