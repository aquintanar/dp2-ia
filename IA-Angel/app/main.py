from fastapi import FastAPI
from pydantic import BaseModel
from model.model import recommend_system
from datetime import datetime
import pandas

app=FastAPI()

class todosItem(BaseModel):
    fidCliente :int
    fidCupon:int
    numInteracciones:int
    updatedAt:datetime

class BodyApi(BaseModel):
    idCupon:str
    todos:list[todosItem]



@app.get("/")
def home():
    return {"Health_Check":"Ok","model_version":"Not Ok"}


@app.post("/predict")
def predict(payload:BodyApi):
    recommendation_books = recommend_system(payload.idCupon,payload.todos)
    recommendation_books.to_list()
    return {"books":recommendation_books.to_list()}