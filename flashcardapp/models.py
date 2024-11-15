from django.db import models
from django_softdelete.models import SoftDeleteModel

# Create your models here.
class Flashcard(SoftDeleteModel):
    question = models.CharField(max_length=300)
    answer = models.CharField(max_length=100)
    image = models.ImageField(upload_to='flashcard_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    studyset_instance = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, related_name='flashcards')
    is_ai_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.question

