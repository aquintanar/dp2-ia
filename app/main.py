from fastapi import FastAPI
from pydantic import BaseModel
from model.model import recommend_system
import pandas

app=FastAPI()


class TextIn(BaseModel):
    text:str



@app.get("/")
def home():
    return {"Health_Check":"Ok","model_version":"Not Ok"}


@app.post("/predict")
def predict(payload:TextIn):
    recommendation_books = recommend_system(payload.text)
    recommendation_books.to_list()
    return {"books":recommendation_books.to_list()}