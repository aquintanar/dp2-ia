import pickle
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from datetime import datetime
import json
from sklearn.neighbors import NearestNeighbors
from pydantic import BaseModel
#import seaborn as sns

model = pickle.load(open('model/model.pkl','rb'))
cupones_id =pickle.load(open('model/cupones_id.pkl','rb'))
final_rating =pickle.load(open('model/final_rating.pkl','rb'))
cupon_pivot =pickle.load(open('model/cupon_pivot.pkl','rb'))



def recommend_books(book_name):

    book_list = []


    book_id=np.where(cupon_pivot.index==book_name)[0]
    

    distance,suggestion = model.kneighbors(cupon_pivot.iloc[book_id,:].values.reshape(1,-1),n_neighbors=4)
    for i in range(len(suggestion)):
        books = cupon_pivot.index[suggestion[i]]
    
    return books

class todosItem(BaseModel):
    fidCliente: int
    fidCupon: int
    numInteracciones: int
    updatedAt: datetime



def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")



def recommend_system(idCupon,todos):
    
    todos_dict = [item.dict() for item in todos]
    todos_json = json.dumps(todos_dict,default=custom_serializer,indent=4)

    data=json.loads(todos_json)

    todos_dataframe = pd.DataFrame(data)

    print(todos_dataframe)

    interacciones=pd.read_csv('D:/Recommender System/Inteligencia_Artificial_Angel/dp2-ia/IA-Angel/archivos/Interacciones.csv',sep=',',encoding='latin-1',on_bad_lines='skip')
    
    print(interacciones)

    #interraciones_cliente = interacciones['idCliente']==37

    #interacciones_clientes2=interacciones[interraciones_cliente]

    #cupon_favorito = interacciones_clientes2['Interaccion'].idxmax()
    
    #print(interacciones_clientes2.iloc[cupon_favorito])

    pivote_interacciones=interacciones.pivot_table(columns="idCliente",index="idCupon",values="Interaccion")


    pivote_interacciones.fillna(0,inplace=True)

    pivote_interacciones_resumido = csr_matrix(pivote_interacciones)

    model=NearestNeighbors(algorithm='brute')

    model.fit(pivote_interacciones_resumido)

    distancia,sugerencias = model.kneighbors(pivote_interacciones.iloc[int(1),:].values.reshape(1,-1),n_neighbors=5)

    print(sugerencias)

    respuesta=pd.DataFrame(columns=['CuponFavorito','CuponRecomendado','Prioridad'])
    contadorTotal=0
    prioridad=1


    for i in range(1,interacciones['idCupon'].max()):
        distancia,sugerencias = model.kneighbors(pivote_interacciones.iloc[i,:].values.reshape(1,-1),n_neighbors=5)
        for j in sugerencias[0]:
            if i!=j:
                respuesta.loc[contadorTotal]=[i,j,prioridad]
                contadorTotal+=1
                prioridad+=1
        prioridad=1

    print(respuesta)

    valor= int(idCupon)
    recommendation_books =recommend_books(valor)
    return recommendation_books

   