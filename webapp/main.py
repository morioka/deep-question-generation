from fastapi import FastAPI
from ml_api import schemas
from ml_api.ml import MockMLAPI

app = FastAPI(
    title="question-generation API",
    description="this is a <a href='https://huggingface.co/sonoisa/t5-base-japanese-question-generation'>t5-base-japanese-question-generation</a> sample api.",
    version="1.0.0"
)
ml = MockMLAPI()
ml.load() # load weight or model instanse using joblib or pickle

@app.post('/prediction/online', response_model=schemas.Pred)
async def online_prediction(data: schemas.Data):
    preds = ml.predict(data.data)
    return {"prediction": preds}

@app.post('/generate', response_model=schemas.GeneratedQuestionList)
async def generate_questions(answer_context_set: schemas.AnswerContextList):
    generated_questions = ml.generate_questions(answer_context_set.answer_context)
    return {"questions": [{"question": question} for question in generated_questions]}

