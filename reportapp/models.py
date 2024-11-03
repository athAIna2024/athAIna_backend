from django.db import models

# Create your models here.
class TestResult(models.Model):
    generated_test_instance = models.ForeignKey('testapp.GeneratedTest', on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField()
    overall_score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.submitted_at