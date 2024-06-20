import pickle
import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from datetime import datetime,timedelta
import json
from sklearn.neighbors import NearestNeighbors
from pydantic import BaseModel
import requests
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

url='http://localhost:3000/api/cupones/nuevaRecomendacionGeneral'




#import seaborn as sns

model = pickle.load(open('model/model.pkl','rb'))
cupones_id =pickle.load(open('model/cupones_id.pkl','rb'))
final_rating =pickle.load(open('model/final_rating.pkl','rb'))
cupon_pivot =pickle.load(open('model/cupon_pivot.pkl','rb'))

ps= PorterStemmer()

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

def remove_space(word):
    l=[]
    for i in word:
        l.append(i.replace(" ",""))
    return l

def stems(text):
    l=[]
    for i in text.split():
        l.append(ps.stem(i))
    return " ".join(l)


def content_based_filtering(todos):
    todos_dict = [item.dict() for item in todos]
    todos_json = json.dumps(todos_dict,default=custom_serializer,indent=4)

    data=json.loads(todos_json)

    todos_dataframe = pd.DataFrame(data)
    

    todos_dataframe['sumilla'] = todos_dataframe['sumilla'].apply(lambda x:x.split())
    todos_dataframe['descripcionCompleta'] = todos_dataframe['descripcionCompleta'].apply(lambda x:x.split())

   

    todos_dataframe['locatarioNombre'] =todos_dataframe['locatarioNombre'].str.split(',')

    todos_dataframe['locatarioNombre'] = todos_dataframe['locatarioNombre'].apply(remove_space)
    todos_dataframe['categoriaTiendaNombre']=todos_dataframe['categoriaTiendaNombre'].str.split(',')
    
    
    todos_dataframe['tags'] = todos_dataframe['sumilla']+todos_dataframe['descripcionCompleta']+todos_dataframe['locatarioNombre']+todos_dataframe['categoriaTiendaNombre']

    new_df = todos_dataframe[['idCupon','tags']]

    new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))

    new_df['tags']= new_df['tags'].apply(lambda x:x.lower())

    


    new_df['tags']=new_df['tags'].apply(stems)

    cv = CountVectorizer(max_features=5000)

    vector = cv.fit_transform(new_df['tags']).toarray()

    
    similary = cosine_similarity(vector)


    print(similary.shape)
    
    idCuponesPresentes = todos_dataframe['idCupon'].unique()
    print(idCuponesPresentes)
    respuesta=pd.DataFrame(columns=['CuponFavorito','CuponRecomendado','Prioridad'])
    contadorTotal=0
    prioridad=1

    contadorenArreglo=0
    for i in range(1,todos_dataframe['idCupon'].max()):
        if i in idCuponesPresentes:
            print(i)  
            distancias = sorted(list(enumerate(similary[contadorenArreglo])),reverse=True,key=lambda x:x[1])
            
            for j in distancias[1:5]:
                respuesta.loc[contadorTotal]=[i,j[0],prioridad]
                contadorTotal+=1
                prioridad+=1
            prioridad=1
            contadorenArreglo+=1
    
    print(respuesta)

    for index,row in  respuesta.iterrows():
        
        data={
            "cuponFavorito":int(row['CuponFavorito']),
            "cuponRecomendado":int(row['CuponRecomendado']),
            "prioridad": int(row['Prioridad']),
            "tipoAlgoritmo":2
        }
        print(data) 
        print('=====================================')  
        try:
            response = requests.post(url,json=data)
            if response.status_code == 200 or response.status_code == 201:
                data_response= response.json()
                print("Respuesta recibida :")
                print(data_response)
            else:     
                print(f"Error al llamar a la API: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud HTTP para índice")
    return 'hola'


def collaborative_filtering(todos):
    
    todos_dict = [item.dict() for item in todos]

    todos_json = json.dumps(todos_dict,default=custom_serializer,indent=4)

    data=json.loads(todos_json)

    todos_dataframe = pd.DataFrame(data)

    todos_dataframe['dia']= pd.to_datetime(todos_dataframe['dia'])
    
    todos_dataframe['numInteraccionesEstandarizado']=todos_dataframe.apply(lambda row: row['numInteracciones']*1 if datetime.now()-row['dia']<= timedelta(days=5) else(row['numInteracciones']*0.5 if(datetime.now()-row['dia']<= timedelta(days=10) and datetime.now()-row['dia']> timedelta(days=5)) else 0),axis=1)

    interacciones = todos_dataframe.groupby(['fidCliente','fidCupon']).agg(numInteracciones=('numInteraccionesEstandarizado','sum')).reset_index()

    

    interacciones=interacciones.rename(columns={'fidCliente':'idCliente'})
    interacciones=interacciones.rename(columns={'fidCupon':'idCupon'})
    interacciones=interacciones.rename(columns={'numInteracciones':'Interaccion'})
 

    pivote_interacciones=interacciones.pivot_table(columns="idCliente",index="idCupon",values="Interaccion")

    print(pivote_interacciones)

    pivote_interacciones.fillna(0,inplace=True)

    pivote_interacciones_resumido = csr_matrix(pivote_interacciones)

    model=NearestNeighbors(algorithm='brute')

    model.fit(pivote_interacciones_resumido)

    respuesta=pd.DataFrame(columns=['CuponFavorito','CuponRecomendado','Prioridad'])
    contadorTotal=0
    prioridad=1

    idCuponesPresentes = interacciones['idCupon'].unique()
    

    for i in range(1,interacciones['idCupon'].max()):
        if i in idCuponesPresentes:
            print(i)
            distancia,sugerencias = model.kneighbors(pivote_interacciones.iloc[int(16),:].values.reshape(1,-1),n_neighbors=4)
            for j in sugerencias[0]:
                if i!=j:
                    respuesta.loc[contadorTotal]=[i,j,prioridad]
                    contadorTotal+=1
                    prioridad+=1
            prioridad=1

    print(respuesta)

  
    

    for index,row in  respuesta.iterrows():
        
        data={
            "cuponFavorito":int(row['CuponFavorito']),
            "cuponRecomendado":int(row['CuponRecomendado']),
            "prioridad": int(row['Prioridad']),
            "tipoAlgoritmo":1
        }
        print(data) 
        print('=====================================')  
        try:
            response = requests.post(url,json=data)
            if response.status_code == 200 or response.status_code == 201:
                data_response= response.json()
                print("Respuesta recibida :")
                print(data_response)
            else:     
                print(f"Error al llamar a la API: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print("Error al realizar la solicitud HTTP para índice")


    return 'Todo bien'
   