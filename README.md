# 🎬 MoodFlix: Smart Movie Recommender

MoodFlix is an intelligent, high-performance Movie Recommendation Engine featuring a sleek, modern UI inspired by Netflix and Hotstar. It uses machine learning trained on TMDB datasets to deliver hyper-personalized movie suggestions.

## 🚀 Live Demo
(https://moodflixmovierec.streamlit.app/)

## 🧠 The Recommendation Engines
Under the hood, MoodFlix runs three distinct analysis algorithms to suggest the perfect movie:

1. **Content-Based Filtering (The Mood Quiz):** Uses `TfidfVectorizer` and Cosine Similarity to break down movie genres mathematically, letting you discover movies similar to your favorite action, comedy, or horror styles.
2. **Collaborative Filtering:** Generates a vast User-Movie Matrix tracking human behavior. By simulating a specific 'User ID', it matches your history against other real users to find your "taste twins", recommending movies they rated highly but you haven't seen yet.
3. **K-Nearest Neighbors (KNN):** Uses Scikit-learn's `NearestNeighbors` Machine Learning model to plot user watch history into multi-dimensional space, accurately mapping the closest users to your specific profile.

## ⚡ Performance Architecture
- **Asynchronous API Fetching:** Deploys a Python `ThreadPoolExecutor` to query the TMDB API across 10 concurrent threads simultaneously, reducing poster load times from ~15 seconds to under a second.
- **Session Caching:** Implements Streamlit's `@st.cache_data` memory caching to ensure homepage trends and category models remain instantaneous without unneeded API saturation.

## 🛠️ Built With
- **Frontend:** Streamlit, HTML/CSS
- **Backend/ML:** Python, Pandas, Scikit-learn
- **Data Source:** TMDB 5000 Movie Dataset

## 💻 Running Locally

1. Create a virtual environment and install dependencies:
```bash
pip install -r requirements.txt
```
2. Start the Streamlit application:
```bash
streamlit run app.py
```
