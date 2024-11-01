from django.db import models

# Create your models here.
class TestResult(models.Model):
    studyset_id = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, related_name='testresult')
    learner_id = models.ForeignKey('accountapp.Learner', on_delete=models.CASCADE, related_name='testresult')
    score = models.IntegerField()
    overall_score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.learner.user.username + ' ' + self.studyset_chosen.title