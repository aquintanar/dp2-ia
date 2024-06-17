import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

movies = pd.read_csv('D:/Recommender System/Inteligencia_Artificial_Angel/dp2-ia/Content-Based/archivos/tmdb_5000_movies.csv',sep=',',encoding='latin-1',on_bad_lines='skip')
credits = pd.read_csv('D:/Recommender System/Inteligencia_Artificial_Angel/dp2-ia/Content-Based/archivos/tmdb_5000_credits.csv',sep=',',encoding='latin-1',on_bad_lines='skip')

print(movies)
print(credits)