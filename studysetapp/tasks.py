from celery import shared_task
from celery.exceptions import Retry
from .pymupdf_utils import convert_pdf_to_images, extract_data_from_pdf
from .google_geminiai_utils import generate_data_for_flashcards, clean_data_for_flashcard_creation

@shared_task
def convert_pdf_to_images_task(file_name):
    return convert_pdf_to_images(file_name)
@shared_task
def extract_data_from_pdf_task(file_name, page_numbers=[]):
    return extract_data_from_pdf(file_name, page_numbers)
@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 65})
def generate_flashcards_task(extracted_data):
    try:
        return generate_data_for_flashcards(extracted_data)
    except Exception as e:
        raise Retry(exc=e)
@shared_task
def clean_data_for_flashcard_creation_task(valid_flashcards, studyset_id):
    return clean_data_for_flashcard_creation(valid_flashcards, studyset_id)