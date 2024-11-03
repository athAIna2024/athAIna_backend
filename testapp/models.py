from django.db import models

class GeneratedTest(models.Model):
    studyset_instance = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, null=True, blank=True)
    learner_instance = models.ForeignKey('accountapp.Learner', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    flashcard_instance = models.ForeignKey('flashcardapp.Flashcard', on_delete=models.CASCADE, null=True, blank=True)
    learner_answer = models.CharField(max_length=100, blank=True, null=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.studyset_instance} - {self.learner_instance} - {self.created_at}'