from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption, WordFormatOption
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.models.tesseract_ocr_model import TesseractOcrOptions


from django.core.files.storage import FileSystemStorage
from django.conf import settings
from pathlib import Path
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')
django.setup()


pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.ocr_options = TesseractOcrOptions()

# Set up the DocumentConverter
doc_converter = DocumentConverter(
    allowed_formats=[
        InputFormat.PDF,
        InputFormat.DOCX,
        InputFormat.PPTX,
    ],
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=StandardPdfPipeline, backend=PyPdfiumDocumentBackend
        ),
        InputFormat.DOCX: WordFormatOption(
            pipeline_cls=SimplePipeline
        ),
    },
)


def extract_data_from_document(file_name):
    fs = FileSystemStorage(location=settings.MEDIA_ROOT / 'documents')
    file_path = fs.path(file_name + "_selected_pages.pdf")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    converted_results = doc_converter.convert(Path(file_path))
    return converted_results.document.export_to_markdown()

print(extract_data_from_document('Networking_Module_8_to_10'))