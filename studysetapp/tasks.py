from io import BytesIO

from celery import shared_task, group
from .pymupdf_utils import extract_data_from_pdf
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import fitz  # PyMuPDF
import base64
@shared_task
def extract_data_from_pdf(file_name, page_number):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    pdf_path = fs.path(file_name)

    response = {}
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {file_name}")

        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number - 1)
        text = page.get_text()
        response['text'] = text
        response['status'] = 'success'
    except FileNotFoundError as fnf_error:
        response['error'] = str(fnf_error)
        response['status'] = 'failure'
    except Exception as e:
        response['error'] = "Failed to extract text from pdf page: " + str(e)
        response['status'] = 'failure'

    return response

@shared_task
def extract_data_from_pdf_task(file_name, page_numbers=[]):
    response = {}
    try:
        page_numbers = [int(page_number) for page_number in page_numbers]

        tasks = [extract_data_from_pdf.s(file_name, page_number) for page_number in page_numbers]
        task_group = group(tasks)
        results = task_group.apply_async().get()

        text = "".join(result for result in results if isinstance(result, str))
        response['text'] = text
        response['status'] = 'success'
        return response
    except Exception as e:
        response['error'] = "Failed to extract text from document: " + str(e)
        response['status'] = 'failure'
        return response

@shared_task
def convert_pdf_to_images(file_name, page_number):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT)
    pdf_path = fs.path(file_name)

    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number - 1)
        pix = page.get_pixmap()

        img_base64 = base64.b64encode(pix.tobytes()).decode('utf-8')
        return img_base64

    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF page to image: {e}")

@shared_task
def convert_pdf_to_images_task(file_name, page_numbers=[]):
    try:
        page_numbers = [int(page_number) for page_number in page_numbers]

        tasks = [convert_pdf_to_images.s(file_name, page_number) for page_number in page_numbers]
        task_group = group(tasks)
        results = task_group.apply_async().get()

        images = []
        for result in results:
            if isinstance(result, str):
                images.append(result)
        return results
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to images: {e}")


