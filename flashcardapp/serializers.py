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
        fields = ['question', 'answer', 'image', 'studyset_instance', 'created_at', 'updated_at']
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
            'required': 'Please provide an answer',
            'blank': 'Please provide an answer',
            'max_length': 'Please keep the answer under 100 characters.'
        })

    image = serializers.ImageField(
        required=False,
        validators=[validate_image_size],
        error_messages={
            'invalid_image': 'Please provide a valid image file.',
        })


class BulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = []
        for attrs in validated_data:
            # Ensure primary key is not set manually
            if 'id' in attrs:
                del attrs['id']
            result.append(self.child.create(attrs))

        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)

        return result

    def update(self, instances, validated_data):
        instance_hash = {index: instance for index, instance in enumerate(instances)}
        result = [
            self.child.update(instance_hash[index], attrs)
            for index, attrs in enumerate(validated_data)
        ]

        writable_fields = [
            x
            for x in self.child.Meta.fields
            if x not in self.child.Meta.read_only_fields + ("studyset_instance",)
        ]
        if "updated_at" in self.child.Meta.fields:
            writable_fields += ["updated_at"]

        try:
            self.child.Meta.model.objects.bulk_update(result, writable_fields)
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