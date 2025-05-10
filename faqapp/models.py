from django.db import models
from django_softdelete.models import SoftDeleteModel

# Create your models here.
class FAQ(SoftDeleteModel):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.question[:10]} - {self.question[:10]}"

    class Meta:
        db_table = 'faqs'