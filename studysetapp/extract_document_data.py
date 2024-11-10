import os
import django
import PyPDF2
from django.core.files.storage import FileSystemStorage
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')
django.setup()

def extract_data_from_pdf(file_name):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'documents')
    pdf_path = fs.path(file_name + '_selected_pages.pdf')

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")
