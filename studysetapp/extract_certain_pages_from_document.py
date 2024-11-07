import docx
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import django
import PyPDF2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')
django.setup()

def extract_pdf_pages(file_name, page_numbers):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'documents')
    pdf_path = fs.path(file_name)

    reader = PyPDF2.PdfReader(open(pdf_path, 'rb'))
    writer = PyPDF2.PdfWriter()

    for page_num in page_numbers:
        writer.add_page(reader.pages[page_num - 1])

    output_path = pdf_path.replace('.pdf', '_selected_pages.pdf')
    with open(output_path, 'wb') as output_pdf:
        writer.write(output_pdf)

    return output_path

# Example usage
file_name = 'Networking_Module_8_to_10.pdf'
selected_pages = [1, 3]  # Pages to extract
output_pdf_path = extract_pdf_pages(file_name, selected_pages)
print(f'Selected pages saved to: {output_pdf_path}')