from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import django
import PyPDF2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')
django.setup()

def extract_document_data(file_name):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'documents')
    pdf_path = fs.path(file_name + '_selected_pages.pdf')

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


# Example usage
file_name = 'Networking_Module_8_to_10'
print(extract_document_data(file_name))