from django.db import models
from django.utils.translation import gettext_lazy as _

class StudySet(models.Model):
    class SubjectChoices(models.TextChoices): # Enumerating the choices for the subjects
        ARTS = 'ARTS', _('Arts')
        BUSINESS = 'BUS', _('Business')
        GEOGRAPHY = 'GEO', _('Geography')
        ENGINEERING = 'ENGR', _('Engineering')
        HEALTH_MEDICINE = 'HEALTH_MED', _('Health and Medicine')
        HISTORY = 'HIST', _('History')
        LAW_POLITICS = 'LAW_POL', _('Law and Politics')
        LANGUAGES_CULTURES = 'LANG_CULT', _('Languages and Cultures')
        MATHEMATICS = 'MATH', _('Mathematics')
        PHILOSOPHY = 'PHIL', _('Philosophy')
        SCIENCE = 'SCI', _('Science')
        SOCIAL_SCIENCES = 'SOC_SCI', _('Social Sciences')
        TECHNOLOGY = 'TECH', _('Technology')
        WRITING_LITERATURE = 'WRIT_LIT', _('Writing and Literature')

    title = models.CharField(max_length=60)
    description = models.CharField(max_length=100)
    subjects = models.CharField(max_length=20, choices=SubjectChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PDF(models.Model):
    pdf = models.FileField(upload_to='pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    studyset_instance = models.ForeignKey('studysetapp.StudySet', on_delete=models.CASCADE, related_name='pdfs')

    def __str__(self):
        return f"PDF {self.id}"