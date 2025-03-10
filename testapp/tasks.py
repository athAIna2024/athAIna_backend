from celery import shared_task
from .google_gemini_ai_utils import validate_learner_answer_with_ai

@shared_task
def validate_learner_answer_with_ai_task(question, correct_answer, learner_answer):
    return validate_learner_answer_with_ai(question, correct_answer, learner_answer)