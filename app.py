import streamlit as st
from train_model import recommend_collab, recommend_content, content_data, recommend_knn
import requests
import re

API_KEY = "0ccb32327b5de020e6ea4f8a9f868ca5"
DEFAULT_POSTER = "https://via.placeholder.com/200x300.png?text=No+Image"

st.set_page_config(layout="wide")

# =========================
# STYLING
# =========================
# =========================
# STYLING (Netflix Style)
# =========================
st.markdown("""
<style>
/* Setup natural padding for all elements */
.block-container {
    padding: 0rem 4rem !important;
}
/* Netflix dark background */
div.stApp {
    background-color: #141414;
    color: white;
}
/* Hide standard header */
header[data-testid="stHeader"] {
    background-color: transparent;
}
/* Custom Navbar */
.navbar {
    padding: 1.5rem 4rem;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    z-index: 999;
}
.navbar-logo {
    color: #E50914;
    font-size: 2.5rem;
    font-weight: 800;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    letter-spacing: 1px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}
/* Hero Section */
.hero-section {
    position: relative;
    height: 70vh;
    background-size: cover;
    background-position: center;
    background-image: linear-gradient(to right, rgba(20,20,20,1) 0%, rgba(20,20,20,0.5) 50%, rgba(20,20,20,0) 100%), linear-gradient(to top, #141414 0%, rgba(20,20,20,0) 20%), url('https://image.tmdb.org/t/p/original/mrzGgOoGi5mZglE4oiof4xAaQz8.jpg'); /* Interstellar backdrop as placeholder */
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 4rem;
    margin-bottom: -40px;
    margin-left: -4rem;
    margin-right: -4rem;
}
.hero-title {
    font-size: 5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
}
.hero-desc {
    font-size: 1.2rem;
    max-width: 600px;
    margin-bottom: 2rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    line-height: 1.5;
}
.hero-btn {
    background-color: white;
    color: black;
    border: none;
    padding: 0.8rem 2rem;
    font-size: 1.2rem;
    font-weight: bold;
    border-radius: 4px;
    cursor: auto;
    margin-right: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.hero-btn.more-info {
    background-color: rgba(109, 109, 110, 0.7);
    color: white;
}

/* Movie Rows */
.movie-category-title {
    font-size: 1.4vw;
    font-weight: 800;
    margin-left: 0;
    margin-bottom: 10px;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #e5e5e5;
}
.movie-row {
    display: flex;
    overflow-x: auto;
    padding: 10px 0 40px 0;
    gap: 15px;
    scroll-behavior: smooth;
    scrollbar-width: thin;
    scrollbar-color: #333 #141414;
}
.movie-row::-webkit-scrollbar {
    height: 8px;
}
.movie-row::-webkit-scrollbar-track {
    background: #141414;
    border-radius: 4px;
}
.movie-row::-webkit-scrollbar-thumb {
    background: #333;
    border-radius: 4px;
}
.movie-row::-webkit-scrollbar-thumb:hover {
    background: #555;
}
.movie-card {
    position: relative;
    flex: 0 0 auto;
    width: 15vw;
    min-width: 160px;
    max-width: 220px;
    border-radius: 4px;
    transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    cursor: pointer;
}
.movie-card img {
    width: 100%;
    border-radius: 4px;
    display: block;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.overlay {
    position: absolute;
    bottom: 0;
    background: linear-gradient(to top, rgba(20,20,20,1) 0%, rgba(20,20,20,0.9) 30%, rgba(20,20,20,0) 100%);
    color: white;
    width: 100%;
    height: 100%;
    opacity: 0;
    font-size: 0.8rem;
    padding: 10px;
    border-radius: 4px;
    transition: opacity 0.3s;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}
.movie-card:hover {
    transform: scale(1.15) translateY(-10px);
    z-index: 10;
}
.movie-card:hover .overlay {
    opacity: 1;
}

/* Hide Streamlit Default Forms */
[data-testid="stForm"] {
    border: none;
    padding: 0;
}

/* Quiz padding */
.quiz-container {
    padding: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Navbar and Hero Injection
st.markdown("""
<div class="navbar"><div class="navbar-logo">MOODFLIX</div></div>
<div class="hero-section">
    <div class="hero-title">Welcome to MoodFlix</div>
    <div class="hero-desc">Discover your next favorite movie. Tailored strictly to your mood, taste, and what you love. Endless entertainment awaits.</div>
    <div>
        <button class="hero-btn">▶ Play</button>
        <button class="hero-btn more-info">ℹ More Info</button>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# CLEAN TITLE
# =========================
def clean_title(title):
    title = re.sub(r"\(\d{4}\)", "", title)
    if ", The" in title:
        title = "The " + title.replace(", The", "")
    if ", A" in title:
        title = "A " + title.replace(", A", "")
    return title.strip()

# =========================
# POSTER
# =========================
@st.cache_data(show_spinner=False)
def fetch_poster(movie_title):
    try:
        movie_title = clean_title(movie_title)
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
        data = requests.get(url).json()

        if data["results"]:
            poster = data["results"][0].get("poster_path")
            if poster:
                return "https://image.tmdb.org/t/p/w500/" + poster
        return DEFAULT_POSTER
    except:
        return DEFAULT_POSTER

# =========================
# DETAILS
# =========================
@st.cache_data(show_spinner=False)
def fetch_details(movie_title):
    try:
        movie_title = clean_title(movie_title)
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
        data = requests.get(url).json()

        if data["results"]:
            movie = data["results"][0]
            return movie.get("vote_average", "N/A"), movie.get("overview", "No description")

        return "N/A", "No description"
    except:
        return "N/A", "No description"

# =========================
# HOVER CARD
# =========================
# =========================
# MOVIE ROW RENDERING
# =========================
def get_movie_card_html(movie):
    poster = fetch_poster(movie)
    rating, overview = fetch_details(movie)
    return f"""
    <div class="movie-card">
        <img src="{poster}" alt="{movie}">
        <div class="overlay">
            <strong>{movie}</strong><br>
            ⭐ {rating}<br>
            {overview[:80]}...
        </div>
    </div>
    """

def show_movie_row(title, movies_list):
    cards_html = "".join([get_movie_card_html(m) for m in movies_list])
    html = f"""
    <div class="movie-category-title">{title}</div>
    <div class="movie-row">
        {cards_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# =========================
# TRENDING
# =========================
@st.cache_data(show_spinner=False)
def get_trending_movies():
    return content_data.sample(8)['title'].tolist()

trending_movies = get_trending_movies()
show_movie_row("Trending Now", trending_movies)

# =========================
# QUIZ
# =========================
st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
st.subheader("Not sure what to watch? Take a quiz!")

with st.form("quiz_form"):
    col1, col2 = st.columns(2)
    with col1:
        genre = st.selectbox("Choose genre", ["Action","Comedy","Drama","Horror","Romance"])
    with col2:
        mood = st.selectbox("Mood", ["Happy","Sad","Excited","Scared","Relaxed"])
    
    quiz_submitted = st.form_submit_button("Get Recommendations")

if quiz_submitted:

    if mood == "Scared":
        genre = "Horror"
    elif mood == "Happy":
        genre = "Comedy"
    elif mood == "Sad":
        genre = "Drama"
    elif mood == "Excited":
        genre = "Action"
    elif mood == "Relaxed":
        genre = "Romance"

    filtered = content_data[
        content_data['genres'].str.contains(genre, case=False, na=False)
    ]

    recs = filtered.sample(min(8, len(filtered)))['title'].tolist()
    show_movie_row(f"Because you are feeling {mood}...", recs)
st.markdown('</div>', unsafe_allow_html=True)

# =========================
# CATEGORY FUNCTION
# =========================
@st.cache_data(show_spinner=False)
def get_category_movies(genre):
    filtered = content_data[
        content_data['genres'].str.contains(genre, case=False, na=False)
    ]
    return filtered.sample(min(10, len(filtered)))['title'].tolist()

def show_category(title, genre):
    movies = get_category_movies(genre)
    show_movie_row(title, movies)

# =========================
# CATEGORIES BACK 🔥
# =========================
show_category("Horror Movies", "Horror")
show_category("Comedy Movies", "Comedy")
show_category("Family Movies", "Children")
show_category("Fantasy Movies", "Fantasy")
show_category("Kids Movies", "Animation")

# =========================
# SIDEBAR (KNN DEFAULT)
# =========================
option = st.sidebar.selectbox(
    "Recommendation Type",
    [
        "KNN Recommendation",
        "Collaborative (User Based)",
        "Content Based (Movie Based)"
    ]
)

# Sidebar styling
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #1a1a1a;
}
</style>
""", unsafe_allow_html=True)

# =========================
# KNN DEFAULT
# =========================
st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
if option == "KNN Recommendation":
    with st.form("knn_form"):
        user_id = st.number_input("User ID", min_value=1)
        knn_submitted = st.form_submit_button("Recommend")

    if knn_submitted:
        recs = recommend_knn(user_id)
        if recs:
            show_movie_row(f"KNN Recommendations for User {user_id}", recs)

elif option == "Collaborative (User Based)":
    with st.form("collab_form"):
        user_id = st.number_input("User ID", min_value=1)
        collab_submitted = st.form_submit_button("Recommend")

    if collab_submitted:
        recs = recommend_collab(user_id)
        if recs:
            show_movie_row(f"Collaborative Recommendations for User {user_id}", recs)

else:
    with st.form("content_form"):
        movie = st.selectbox("Movie", content_data['title'])
        content_submitted = st.form_submit_button("Recommend")

    if content_submitted:
        recs = recommend_content(movie)
        if recs:
            show_movie_row(f"Because you watched {movie}", recs)
st.markdown('</div>', unsafe_allow_html=True)