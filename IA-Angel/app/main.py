from fastapi import FastAPI
from pydantic import BaseModel
from model.model import collaborative_filtering
from model.model import content_based_filtering
from datetime import datetime
import pandas

app=FastAPI()

class interaccionItem(BaseModel):
    fidCliente :int
    fidCupon:int
    numInteracciones:int
    tipo:str
    dia:datetime

class CollaborativeApi(BaseModel):
    todos:list[interaccionItem]

class cuponItem(BaseModel):
    idCupon:int
    sumilla:str
    descripcionCompleta:str
    costoPuntos:int
    esLimitado:bool
    cantidadDisponible:int
    idLocatario:int
    locatarioNombre:str
    categoriaTiendaID:int
    categoriaTiendaNombre:str

class ContentApi(BaseModel):
    cupones:list[cuponItem]

@app.get("/")
def home(): 
    return {"Health_Check":"Ok","model_version":"Not Ok"}


@app.post("/collaborative_filtering")
def predict(payload:CollaborativeApi):
    collaborative_filtering(payload.todos)
    return 'Todo bien'

@app.post("/content_based_filtering")
def predict(payload:ContentApi):
    content_based_filtering(payload.cupones)
    return 'Todo bien'