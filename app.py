import streamlit as st
import pickle 
import pandas as pd
import requests


# Page configuration
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load the movies data
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))
movies_list = movies["title"].values 


# Fetch poster from TMDB API
def fetch_poster(movie_id):
    API_KEY = "a4ca7366efe2e558aa8f2fffe23d3ca9"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return full_path
        return None
    except Exception as e:
        return None


# Recommend movies based on similarity
def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_posters


# Header Section
st.title("Movie Recommender System")
st.markdown("### Discover your next favorite movie")
st.divider()

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("#### Select a movie you enjoy")
    selected_movies_name = st.selectbox(
        "Search from thousands of movies:",
        movies_list,
        index=None,
        placeholder="Type or select a movie...",
        label_visibility="collapsed"
    )
    
    st.markdown("")  # Spacing
    
    # Center the button
    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
    with button_col2:
        recommend_button = st.button("Recommend", use_container_width=True, type="primary")

st.divider()

# Recommendations Section
if recommend_button:
    if selected_movies_name:
        with st.spinner("🔍 Finding perfect matches for you..."):
            names, posters = recommend(selected_movies_name)
        
        st.success(f" Based on **{selected_movies_name}**, you might also enjoy:")
        st.markdown("")  # Spacing
        
        # Display recommendations in cards
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                # Create a card-like container
                with st.container():
                    if posters[idx]:
                        st.image(posters[idx], use_container_width=True)
                    else:
                        st.info("🖼️ Poster unavailable")
                    
                    st.markdown(f"**{names[idx]}**")
                    st.caption(f"Recommendation #{idx + 1}")
    else:
        st.warning("⚠️ Please select a movie first!")

# Footer
st.divider()
st.markdown("")
st.markdown("")

footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col2:
    st.caption("Powered by TMDB API | Built with Streamlit")
    st.caption("💡 Tip: Try different movies to explore more recommendations!")