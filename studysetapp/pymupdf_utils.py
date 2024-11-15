import os
import django
import fitz  # PyMuPDF
from django.core.files.storage import FileSystemStorage
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')
django.setup()

def create_new_pdf_for_selected_pages(file_name, page_numbers):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'documents')
    pdf_path = fs.path(file_name)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        output_doc = fitz.open()

        for page_num in page_numbers:
            if 0 < page_num <= len(doc):
                output_doc.insert_pdf(doc, from_page=page_num - 1, to_page=page_num - 1)

        output_path = pdf_path.replace('.pdf', '_selected_pages.pdf')
        output_doc.save(output_path)
        output_doc.close()
    except FileNotFoundError as e:
        raise FileNotFoundError(f"File not found: {pdf_path}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}")
    return output_path

def extract_data_from_pdf(file_name, page_numbers): # Docling more advanced than PyMuPDF
    fs = FileSystemStorage(location=settings.MEDIA_ROOT) # removed / 'documents' (you can add it for debugging)
    pdf_path = fs.path(file_name + "_selected_pages.pdf")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {file_name}")

    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in page_numbers:
            if 0 < page_num <= len(doc):
                page = doc.load_page(page_num - 1)
                text += page.get_text()
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from document: {e}")


def convert_pdf_to_images(file_name):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT) # removed / 'documents' (you can add it for debugging)
    pdf_path = fs.path(file_name)

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {file_name}")

    try:
        doc = fitz.open(pdf_path)
        images = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            images.append(pix)
        return images
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to images: {e}")



