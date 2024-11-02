from rest_framework.exceptions import ValidationError
from studysetapp.models import StudySet
MEGA_BYTE_LIMIT = 0.5
def validate_image_size(image):
    filesize = image.size

    # Multiplying by 1024 to convert KB to bytes
    if filesize > MEGA_BYTE_LIMIT * 1024:
        raise ValidationError(f'Please keep the image size under {MEGA_BYTE_LIMIT} KB.')


def validate_studyset_id(value):
    if not StudySet.objects.filter(id=value).exists():
        raise ValidationError(f'StudySet with {value} does not exist.')