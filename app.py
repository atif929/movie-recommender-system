import streamlit as st
import pickle
import requests

# Page configuration
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide"
)

# Load the pre-computed data
@st.cache_data
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

# Load data
movies, similarity = load_data()
movies_list = movies["title"].values

# Fetch movie poster from TMDB API
def fetch_poster(movie_id):
    API_KEY = "a4ca7366efe2e558aa8f2fffe23d3ca9"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    
    try:
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None
    except:
        return None

# Recommendation function
def recommend(movie):
    try:
        # Find movie index
        movie_index = movies[movies["title"] == movie].index[0]
        
        # Get similarity scores
        distances = similarity[movie_index]
        
        # Sort and get top 5 similar movies (excluding the movie itself)
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommended_movies = []
        recommended_posters = []
        
        for i in movie_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))
        
        return recommended_movies, recommended_posters
    except:
        return [], []

# UI Layout
st.markdown("# 🎬 Movie Recommender System")
st.markdown("### Discover your next favorite movie")
st.divider()

# Main selection area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("#### Select a movie you enjoy")
    selected_movie = st.selectbox(
        "Search from thousands of movies:",
        movies_list,
        index=None,
        placeholder="Type or select a movie...",
        label_visibility="collapsed"
    )
    
    st.markdown("")
    
    # Center the button
    button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
    with button_col2:
        recommend_button = st.button("Recommend", 
                                     use_container_width=True, 
                                     type="primary")

st.divider()

# Recommendations display
if recommend_button:
    if selected_movie:
        with st.spinner("🔍 Finding perfect matches for you..."):
            names, posters = recommend(selected_movie)
        
        if names:
            st.success(f"Based on **{selected_movie}**, you might also enjoy:")
            st.markdown("")
            
            # Display in 5 columns
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                with col:
                    with st.container():
                        if posters[idx]:
                            st.image(posters[idx], use_container_width=True)
                        else:
                            st.info("🖼️ Poster unavailable")
                        
                        st.markdown(f"**{names[idx]}**")
                        st.caption(f"Recommendation #{idx + 1}")
        else:
            st.error("❌ Could not find recommendations. Please try another movie.")
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