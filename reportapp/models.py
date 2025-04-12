from django.db import models
from django.utils import timezone
from django_softdelete.models import SoftDeleteModel

class TestReport(SoftDeleteModel):
    studyset_instance = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, null=True, blank=True)
    batch = models.ForeignKey('testapp.TestBatch', on_delete=models.CASCADE, null=True, blank=True)
    score = models.IntegerField()
    number_of_questions = models.IntegerField()
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'test_reports'