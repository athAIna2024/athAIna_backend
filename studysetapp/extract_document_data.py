import os
import django
import PyPDF2
from django.core.files.storage import FileSystemStorage
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')
django.setup()

def extract_data_from_pdf(file_name, page_numbers):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'documents')
    pdf_path = fs.path(file_name)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            text = "".join([reader.pages[page_num - 1].extract_text() for page_num in page_numbers if 0 < page_num <= num_pages])
            return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")


# Example usage
file_name = 'Networking_Module_8_to_10.pdf'
selected_pages = [2, 3]  # Pages to extract
extracted_text = extract_data_from_pdf(file_name, selected_pages)
print(extracted_text)