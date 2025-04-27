from google import genai
from google.genai import types
from google.genai import errors


import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

client = genai.Client(api_key=env('GEMINI_API_KEY'))

system_instruction = (
    "You are a teacher with expertise in various subjects."
    "Your task is to evaluate a learner's answer based on the provided question and its correct answer."
    "Determine if the learner's answer is a valid partial match and whether it can be considered correct."
    "If the learner's answer is correct, return True; otherwise, return False."
    "Take into account the accuracy of spelling and the relevance of the learner's answer to the question."
)

safety_settings = [
    types.SafetySetting(
        category='HARM_CATEGORY_HATE_SPEECH',
        threshold='BLOCK_ONLY_HIGH',
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_HARASSMENT',
        threshold='BLOCK_ONLY_HIGH',
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
        threshold='BLOCK_ONLY_HIGH',
    ),
    types.SafetySetting(
        category='HARM_CATEGORY_DANGEROUS_CONTENT',
        threshold='BLOCK_ONLY_HIGH',
    ),
]

def validate_learner_answer_with_ai(question, correct_answer, learner_answer):
    prompt = (
        f"\nflashcard question: {question}\n"
        f"flashcard answer: {correct_answer}\n"
        f"learner answer: {learner_answer}"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,  #
                max_output_tokens=1,  # means the model will generate a maximum of 5 tokens (equal to 5 words)
                temperature=0.3,  # means the model will be more conservative in its responses
            ),
        )
        if response.text.strip() == "True":
            return True
        return False
    except errors.APIError as e:
        print(f"An error occurred: {e}")


# question = "What protocol is responsible for ensuring reliable and ordered delivery of data over the Internet?"
# correct_answer = "TCP"
# learner_answer = "Transmission Control Protocol"
# print(validate_learner_answer_with_ai(question, correct_answer, learner_answer))

# prompt = "Are you gemini 2.0 flash now? What is the difference between gemini 1.5?"
# response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
# print(response.text)