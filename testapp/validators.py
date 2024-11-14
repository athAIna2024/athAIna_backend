# testapp/validators.py
from rest_framework.exceptions import ValidationError
from flashcardapp.models import Flashcard

def validate_flashcard_count(studyset_instance, number_of_flashcards):
    total_flashcards = Flashcard.objects.filter(studyset_instance=studyset_instance).count()
    if number_of_flashcards > total_flashcards or number_of_flashcards < 1:
        raise ValidationError(f'The study set only has {total_flashcards} flashcards.')