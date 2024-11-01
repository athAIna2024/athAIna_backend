from django.db import models

class StudySet(models.Model):
    SUBJECT_CHOICES = [
        ('ARTS', 'Arts'),
        ('BUS', 'Business'),
        ('GEO', 'Geography'),
        ('ENGR', 'Engineering'),
        ('HEALTH_MED', 'Health and Medicine'),
        ('HIST', 'History'),
        ('LAW_POL', 'Law and Politics'),
        ('LANG_CULT', 'Languages and Cultures'),
        ('MATH', 'Mathematics'),
        ('PHIL', 'Philosophy'),
        ('SCI', 'Science'),
        ('SOC_SCI', 'Social Sciences'),
        ('TECH', 'Technology'),
        ('WRIT_LIT', 'Writing and Literature')
    ]

    title = models.CharField(max_length=60)
    description = models.CharField(max_length=100)
    subjects = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title