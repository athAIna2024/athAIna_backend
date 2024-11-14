from django.db import models

# Create your models here.
class TestResult(models.Model):
    studyset_instance = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField()
    number_of_questions = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.submitted_at