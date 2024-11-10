import os
from rest_framework.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = {'.pdf', '.docx', '.pptx'}
    if ext not in valid_extensions:
        raise ValidationError('The acceptable file type is in .pdf, .docx, or .pptx.')