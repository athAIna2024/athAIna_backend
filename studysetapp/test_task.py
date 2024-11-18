# test_task.py
import django
from studysetapp.tasks import extract_data_from_pdf_task, convert_pdf_to_images_task

django.setup()

result = extract_data_from_pdf_task.apply_async(args=("documents/Networking_Module_8_to_10_4eQchqC.pdf", [1, 3]))
print(result.get())

result = convert_pdf_to_images_task.apply_async(args=("documents/Networking_Module_8_to_10_4eQchqC.pdf", [1, 3]))
