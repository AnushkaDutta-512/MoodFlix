import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# load cleaned data
data = pd.read_csv('data/cleaned.csv')

# =========================
# 🔹 COLLABORATIVE FILTERING
# =========================

user_movie_matrix = data.pivot_table(index='userId', columns='title', values='rating').fillna(0)

user_similarity = cosine_similarity(user_movie_matrix)


def recommend_collab(user_id, n=5):
    user_index = user_movie_matrix.index.tolist().index(user_id)
    
    sim_scores = list(enumerate(user_similarity[user_index]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    sim_users = [i[0] for i in sim_scores[1:6]]
    
    user_movies = user_movie_matrix.loc[user_id]
    watched = user_movies[user_movies > 0].index.tolist()
    
    recommendations = {}
    
    for sim_user in sim_users:
        sim_user_id = user_movie_matrix.index[sim_user]
        sim_user_movies = user_movie_matrix.loc[sim_user_id]
        
        for movie, rating in sim_user_movies.items():
            if movie not in watched and rating > 0:
                if movie not in recommendations:
                    recommendations[movie] = 0
                recommendations[movie] += rating
    
    recommended_movies = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    
    return [movie[0] for movie in recommended_movies[:n]]


# =========================
# 🔹 CONTENT-BASED FILTERING
# =========================

# remove duplicates
content_data = data[['title', 'genres']].drop_duplicates()

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(content_data['genres'])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)


def recommend_content(movie_title, n=5):
    idx = content_data[content_data['title'] == movie_title].index[0]
    
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    movie_indices = [i[0] for i in sim_scores[1:n+1]]
    
    return content_data['title'].iloc[movie_indices].tolist()


# =========================
# TEST
# =========================

if __name__ == "__main__":
    print("Collaborative:", recommend_collab(1))
    print("Content:", recommend_content(content_data['title'].iloc[0]))
# =========================
# 🔥 KNN MODEL (CLEAN VERSION)
# =========================
from sklearn.neighbors import NearestNeighbors

# train model
knn_model = NearestNeighbors(metric='cosine', algorithm='brute')
knn_model.fit(user_movie_matrix)


def recommend_knn(user_id, n=5):

    # safety check
    if user_id not in user_movie_matrix.index:
        return ["User not found"]

    user_index = user_movie_matrix.index.tolist().index(user_id)

    distances, indices = knn_model.kneighbors(
        user_movie_matrix.iloc[user_index].values.reshape(1, -1),
        n_neighbors=6
    )

    similar_users = indices.flatten()[1:]  # remove itself

    recommendations = {}

    # movies already watched
    watched = user_movie_matrix.loc[user_id]
    watched = watched[watched > 0].index.tolist()

    for sim_user in similar_users:
        sim_user_id = user_movie_matrix.index[sim_user]
        sim_user_movies = user_movie_matrix.loc[sim_user_id]

        for movie, rating in sim_user_movies.items():
            if movie not in watched and rating > 0:
                if movie not in recommendations:
                    recommendations[movie] = 0
                recommendations[movie] += rating

    sorted_movies = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)

    return [movie[0] for movie in sorted_movies[:n]]