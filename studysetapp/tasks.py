from io import BytesIO

from celery import shared_task, group
from .pymupdf_utils import extract_data_from_pdf
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import fitz  # PyMuPDF
import base64
@shared_task
def extract_data_from_pdf_task(file_name, page_numbers=[]):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    pdf_path = fs.path(file_name)
    # try:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {file_name}")

    doc = fitz.open(pdf_path)
    text = ""
    for page_num in page_numbers:
        if 0 < page_num <= len(doc):
            page = doc.load_page(page_num - 1)
            text += page.get_text()
    return text
    # except Exception as e:
    #     raise RuntimeError(f"Failed to extract text from document: {e}")

@shared_task
def convert_pdf_to_images_task(file_name):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    pdf_path = fs.path(file_name)

    try:
        doc = fitz.open(pdf_path)
        images = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_base64 = base64.b64encode(pix.tobytes()).decode('utf-8')
            images.append(img_base64)
        return images
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to images: {e}")


