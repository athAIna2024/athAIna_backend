from django.db import models

# Create your models here.
class Flashcard(models.Model):
    question = models.CharField(max_length=300)
    answer = models.CharField(max_length=100)
    image = models.ImageField(upload_to='flashcard_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    studyset_id = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, related_name='flashcards')

    def __str__(self):
        return self.question

class PDF(models.Model):
    pdf = models.FileField(upload_to='pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    studyset_id = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, related_name='pdfs')

    def __str__(self):
        return self.title