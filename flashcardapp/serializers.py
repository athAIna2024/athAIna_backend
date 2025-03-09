from django_softdelete.managers import SoftDeleteQuerySet
from rest_framework import serializers
from studysetapp.models import StudySet
from .models import Flashcard
from .validators import validate_image_size
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

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
        fields = ['id', 'question', 'answer', 'image', 'studyset_instance', 'created_at', 'updated_at', 'is_ai_generated']
        read_only_fields = ['created_at', 'updated_at', 'is_ai_generated', 'deleted_at', 'restored_at', 'transaction_id']

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
            'required': 'Please provide an answer'
            'answer',
            'blank': 'Please provide an answer',
            'max_length': 'Please keep the answer under 100 characters.'
        })

    image = serializers.ImageField(
        required=False,
        allow_null=True,
        validators=[validate_image_size],
        error_messages={
            'invalid_image': 'Please provide a valid image file.',
        })

class BulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [self.child.create(attrs) for attrs in validated_data]

        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)

        return result
class GeneratedFlashcardSerializer(serializers.ModelSerializer):
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
    studyset_instance = serializers.PrimaryKeyRelatedField(
        queryset=StudySet.objects.all(),
        required=True,
        error_messages={
            'required': 'Please choose a study set',
        }
    )
    is_ai_generated = serializers.BooleanField(default=True)

    class Meta:
        model = Flashcard
        fields = ['question', 'answer', 'image', 'studyset_instance', 'created_at', 'updated_at', 'is_ai_generated']
        read_only_fields = ['image', 'created_at', 'updated_at', 'deleted_at', 'restored_at', 'transaction_id']
        list_serializer_class = BulkCreateListSerializer

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Ensure that studyset_instance is correctly represented
        if isinstance(representation.get('studyset_instance'), SoftDeleteQuerySet):
            representation['studyset_instance'] = list(representation['studyset_instance'])
        return representation