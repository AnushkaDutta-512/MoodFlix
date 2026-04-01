import pandas as pd

movies = pd.read_csv('data/movies.csv')
ratings = pd.read_csv('data/ratings.csv')

# 🔥 LIMIT DATA (IMPORTANT)
ratings = ratings.head(100000)

data = pd.merge(ratings, movies, on='movieId')

data.dropna(inplace=True)

data.to_csv('data/cleaned.csv', index=False)

print("✅ Preprocessing Done!")