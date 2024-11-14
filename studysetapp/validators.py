import os
from rest_framework.exceptions import ValidationError
from .extract_certain_pages_from_document import extract_pdf_page_count

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = {'.pdf'}
    if ext not in valid_extensions:
        raise ValidationError('The acceptable file type is in .pdf')

def validate_pdf_pages(value):
    file_name = value.name
    page_count = extract_pdf_page_count(file_name)
    if value < 1 or value > page_count:
        raise ValidationError(f'Please provide a page number between 1 and {page_count}')