from django_softdelete.models import SoftDeleteModel
from django.db import models
import uuid
class GeneratedTest(SoftDeleteModel, models.Model):
    batch = models.ForeignKey('TestBatch', on_delete=models.CASCADE, null=True, blank=True)
    flashcard_instance = models.ForeignKey('flashcardapp.Flashcard', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)  # Removed auto_now_add
    learner_answer = models.CharField(max_length=100, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    corrected_at = models.DateTimeField(null=True, blank=True)  # Removed auto_now

    def __str__(self):
        return f"{self.flashcard_instance} - {self.batch_id}"

    class Meta:
        db_table = 'generated_tests'


class TestBatch(models.Model):
    batch_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.batch_id)

    class Meta:
        db_table = 'test_batches'