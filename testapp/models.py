from django_softdelete.models import SoftDeleteModel
from django.db import models
import uuid
class GeneratedTest(SoftDeleteModel, models.Model):
    batch_id = models.UUIDField(default=uuid.uuid4, null=True, blank=True, editable=False)
    studyset_instance = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, null=True, blank=True)
    flashcard_instance = models.ForeignKey('flashcardapp.Flashcard', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    learner_answer = models.CharField(max_length=100, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    corrected_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.studyset_instance.title} - {self.flashcard_instance.question}"

    class Meta:
        db_table = 'generated_tests'