import google.generativeai as genai
import environ
from pathlib import Path
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .extract_document_data import extract_data_from_pdf
from flashcardapp.serializers import GeneratedFlashcardSerializer
from studysetapp.models import StudySet

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

system_instruction = ("You are a tutor specialized in all different kinds of subjects."
                      "You will help your learner to study by generating flashcards for them."
                      "The format of the flashcard is as follows: "
                      "Question:Insert the question here/Answer:Insert the answer here."
                      "Each flashcard should be separated by a new line."
                      "Each question must be as close to 300 characters as possible without exceeding it. Each answer must not exceed 100 characters."
                      "The minimum number of flashcards should be 3 with the maximum of 5 flashcards."
                      "The data for the flashcards will be given to you in prompt."
                      "As much as possible, try to stick with the data given to you in the prompt.")

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

def generate_data_for_flashcards(pdf_file_name):
    text_data = extract_data_from_pdf(pdf_file_name)
    prompt = f"Data: {text_data}"
    response = model.generate_content(
        prompt,
        safety_settings=safety_settings
    )
    flashcards = response.text.strip().split("\n")
    valid_flashcards = []

    for flashcard in flashcards:
        question, answer = flashcard.split("/")
        if len(question) <= 300 and len(answer) <= 100:
            valid_flashcards.append(flashcard)
        else:
            pass

    return "\n".join(valid_flashcards)

def populate_flashcards(studyset_instance, data):
    flashcard_data = data.split("\n")
    flashcard_data = [flashcard.split("/") for flashcard in flashcard_data]
    Studyset_instance = StudySet.objects.get(id=studyset_instance)
    errors = []
    for flashcard in flashcard_data:
        question = flashcard[0].replace("Question:", "").strip()
        answer = flashcard[1].replace("Answer:", "").strip()
        serializer = GeneratedFlashcardSerializer(data={
            'question': question,
            'answer': answer,
            'studyset_instance': Studyset_instance.id
        })
        if serializer.is_valid():
            serializer.save()
        else:
            errors.append(serializer.errors)
    return errors


