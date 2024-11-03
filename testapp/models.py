from django.db import models

# Create your models here.
class GeneratedTest(models.Model):
    studyset_instance = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE)
    learner_instance = models.ForeignKey('accountapp.Learner', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey('flashcardapp.Flashcard', related_name='question_set', on_delete=models.CASCADE)
    answer = models.ForeignKey('flashcardapp.Flashcard', related_name='answer_set', on_delete=models.CASCADE)
    learner_answer = models.CharField(max_length=100, blank=True, null=True)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.studyset_instance} - {self.learner_instance} - {self.created_at}'