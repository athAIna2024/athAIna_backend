from flashcardapp.models import Flashcard

def validate_number_of_flashcards(num_of_flashcards, studyset_instance):
    total_flashcards = Flashcard.objects.filter(studyset_instance=studyset_instance).count()
    if num_of_flashcards < total_flashcards:
        return num_of_flashcards
    if num_of_flashcards > total_flashcards:
        return total_flashcards
    if num_of_flashcards <= 0 and total_flashcards >= 10:
        return 10
