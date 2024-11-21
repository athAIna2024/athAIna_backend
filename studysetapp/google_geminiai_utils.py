import os
import django
import google.generativeai as genai
import environ
from pathlib import Path
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging
from rest_framework.exceptions import ValidationError
# Set the environment variable for Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'athAIna_backend.settings')

# Initialize Django
django.setup()

from flashcardapp.serializers import GeneratedFlashcardSerializer
from .models import StudySet

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

genai.configure(api_key=env("GEMINI_API_KEY"))
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1000,
    "response_mime_type": "text/plain",
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

# ADD TO CRS File the minimum and maximum flashcards generated


model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

def generate_data_for_flashcards(data, studyset_id):
    studyset_title = StudySet.objects.all().filter(id=studyset_id).values('title')
    prompt = ("You are a tutor who generates flashcards for learners."
    "Format: Question:Insert the question here/Answer:Insert the answer here."
    "Each flashcard should be on a new line."
    "Questions: ~300 characters. Answers: <=100 characters."
    "Generate 10-15 flashcards based on the provided data." + data + studyset_title)

    valid_flashcards = []
    try:
        response = model.generate_content(
            prompt,
            safety_settings=safety_settings
        )

        if response is None or response.text == "":
            raise ValidationError("No response received from the API. Please try again.")

        flashcards = response.text.strip().split("\n")

        for flashcard in flashcards:
            if "/" in flashcard:
                question, answer = flashcard.split("/", 1)
                logging.info(f"Question: {question}, Answer: {answer}")
                if len(question) <= 300 and len(answer) <= 100:
                    valid_flashcards.append(flashcard)
    except Exception as e:
        raise RuntimeError(f"An error occurred while generating data for flashcards. {e}")
    except genai.errors.GenerativeAIError as e:
        raise ValidationError(f"The request to the API failed. {e}")
    if valid_flashcards == [] or len(valid_flashcards) < 3:
        raise ValidationError("The API did not generate enough valid flashcards. Please try again.")

    return valid_flashcards

# print(generate_data_for_flashcards("Networking", 1))

def clean_data_for_flashcard_creation(valid_flashcards=[], studyset_id=None):
    flashcard_data = []

    for flashcard in valid_flashcards:
        if "/" in flashcard:
            question, answer = flashcard.split("/", 1)
            flashcard_entry = ({
                'question': question.replace("Question:", "").strip(),
                'answer': answer.replace("Answer:", "").strip(),
                'studyset_instance': studyset_id,  # Ensure this ID exists in your StudySet model
            })
            flashcard_data.append(flashcard_entry)
            # print("Flashcard entry:", flashcard_entry) # Debugging: Print each flashcard entry
    return flashcard_data

# def generate_flashcards(valid_flashcards=[], studyset_id=None):
#     flashcard_data = []
#     try:
#         for flashcard in valid_flashcards:
#             if "/" in flashcard:
#                 question, answer = flashcard.split("/", 1)
#                 flashcard_entry = {
#                     'question': question.replace("Question:", "").strip(),
#                     'answer': answer.replace("Answer:", "").strip(),
#                     'studyset_instance': studyset_id,  # Ensure this ID exists in your StudySet model
#                 }
#                 flashcard_data.append(flashcard_entry)
#                 print("Flashcard entry:", flashcard_entry)  # Debugging: Print each flashcard entry
#
#         serializer = GeneratedFlashcardSerializer(data=flashcard_data, many=True)
#         if serializer.is_valid():
#             serializer.save()
#             return "Flashcards generated successfully."
#         else:
#             raise ValidationError(serializer.errors)
#     except Exception as e:
#         raise RuntimeError(f"An error occurred while generating flashcards. {e}")