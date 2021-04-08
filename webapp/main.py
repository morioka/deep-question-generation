from fastapi import FastAPI
from ml_api import schemas
from ml_api.ml import MockMLAPI

app = FastAPI()
ml = MockMLAPI()
ml.load() # load weight or model instanse using joblib or pickle

@app.post('/prediction/online', response_model=schemas.Pred)
async def online_prediction(data: schemas.Data):
    preds = ml.predict(data.data)
    return {"prediction": preds}
