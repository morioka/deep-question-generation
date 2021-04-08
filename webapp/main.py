from fastapi import FastAPI
from ml_api import schemas
from ml_api.ml import QuestionGenerationAPI

app = FastAPI(
    title="question-generation API",
    description="this is a <a href='https://huggingface.co/sonoisa/t5-base-japanese-question-generation'>t5-base-japanese-question-generation</a> sample api.",
    version="1.0.0"
)
ml = QuestionGenerationAPI()
ml.load()

@app.post('/generate', response_model=schemas.GeneratedQuestionList)
async def generate_questions(answer_context_set: schemas.AnswerContextList):
    generated_questions = ml.generate_questions(answer_context_set.answer_context)
    return {"questions": [{"question": question} for question in generated_questions]}

