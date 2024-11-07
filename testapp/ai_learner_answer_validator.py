import google.generativeai as genai
import environ
from pathlib import Path
from google.generativeai.types import HarmCategory, HarmBlockThreshold

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

genai.configure(api_key=env("GEMINI_API_KEY"))
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 5,  # Lower this value to get shorter responses
  "response_mime_type": "text/plain",
}

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
}

system_instruction = ("You are a teacher specialized in all different kinds of subjects."
                       "You are going to be given with the question and its correct answer to help you evaluate the learner's answer."
                       "You are tasked to validate the learner's answer if their partial match answer is considered correct or not."
                       "If the learner's answer is correct, return True. Otherwise, return False.")

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

def validate_learner_answer_with_ai(question, correct_answer, learner_answer):
    prompt = ("\nflashcard question: " + question + "\n" + "flashcard answer: " + correct_answer + "\n" + "learner answer: " + learner_answer)
    response = model.generate_content(
        prompt,
        safety_settings=safety_settings
    )
    if response.text.strip() == "True":
        return True
    else:
        return False

# question = "What protocol is responsible for ensuring reliable and ordered delivery of data over the Internet?"
# correct_answer = "TCP"
# learner_answer = "Transmission Control Protocol"
# print(validate_learner_answer_with_ai(question, correct_answer, learner_answer))