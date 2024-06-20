import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import ast
import nltk
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv('D:/Recommender System/Inteligencia_Artificial_Angel/dp2-ia/Content-Based/archivos/tmdb_5000_movies.csv',sep=',',encoding='latin-1',on_bad_lines='skip')
credits = pd.read_csv('D:/Recommender System/Inteligencia_Artificial_Angel/dp2-ia/Content-Based/archivos/tmdb_5000_credits.csv',sep=',',encoding='latin-1',on_bad_lines='skip')


movies=movies.merge(credits,on='title')

movies=movies[['movie_id','title','overview','genres','keywords','cast','crew']]

print(movies.shape)

movies.isnull().sum()

movies.dropna(inplace=True)

movies.duplicated().sum()



def convert(text):
    l=[]
    for i in ast.literal_eval(text):
        l.append(i['name'])
    return l

movies['genres']=movies['genres'].apply(convert)
movies['keywords']=movies['keywords'].apply(convert)


def convert_cast(text):
    l=[]
    counter=0
    for i in ast.literal_eval(text):
        if counter < 3:
            l.append(i['name'])
        counter+=1
    return l


movies['cast']=movies['cast'].apply(convert_cast)


def fetch_director(text):
    l=[]
    for i in ast.literal_eval(text):
        if i['job']=='Director':
            l.append(i['name'])
            break
    return l

movies['crew']=movies['crew'].apply(fetch_director)
print(movies['crew'])


movies['overview']=movies['overview'].apply(lambda x:x.split())



def remove_space(word):
    l=[]
    for i in word:
        l.append(i.replace(" ",""))
    return l

movies['cast']=movies['cast'].apply(remove_space)
movies['crew']=movies['crew'].apply(remove_space)
movies['keywords']=movies['keywords'].apply(remove_space)
movies['genres']=movies['genres'].apply(remove_space)

movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

new_df = movies[['movie_id','title','tags']]

new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))

new_df['tags']= new_df['tags'].apply(lambda x:x.lower())


ps= PorterStemmer()

def stems(text):
    l=[]
    for i in text.split():
        l.append(ps.stem(i))
    return " ".join(l)

new_df['tags']=new_df['tags'].apply(stems)

cv = CountVectorizer(max_features=5000,stop_words='english')

vector = cv.fit_transform(new_df['tags']).toarray()

print(vector)

similary = cosine_similarity(vector)

def recommend(movie):
    index= new_df[new_df['title']==movie].index[0]
    distances=sorted(list(enumerate(similary[index])),reverse=True,key=lambda x:x[1])
    for i in distances[1:6]:
        print(new_df.iloc[i[0]].title)


recommend('The Dark Knight Rises')