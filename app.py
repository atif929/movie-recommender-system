import streamlit as st
import pickle
import requests
import os

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="🎬 Movie Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. CUSTOM CSS (FOR STYLING)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main-header {
        text-align: center;
        padding-bottom: 20px;
    }
    
    /* --- UPDATED MOVIE TITLE STYLE --- */
    .movie-title {
        font-size: 16px;       /* Slightly smaller to fit better */
        font-weight: bold;
        text-align: center;
        padding: 5px;          /* Padding inside the box */
        line-height: 1.4;      /* Better spacing for multi-line text */
        
        /* Flexbox centers short titles but expands for long ones */
        display: flex;
        align-items: center; 
        justify-content: center;
        min-height: 60px;      /* Minimum height for symmetry */
        word-wrap: break-word; /* Ensures very long words don't break layout */
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 50px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. AUTO-DOWNLOAD SCRIPT (CRITICAL FOR DEPLOYMENT)
# -----------------------------------------------------------------------------
# REPLACE 'YOUR_USERNAME' and 'YOUR_REPO_NAME' with your actual GitHub details
GITHUB_URL = "https://github.com/atif929/movie-recommender-system/releases/download/v1.0.0/similarity.pkl"
FILENAME = "similarity.pkl"

if not os.path.exists(FILENAME):
    with st.spinner(f"Downloading model file (180MB)... this happens only once!"):
        try:
            response = requests.get(GITHUB_URL, stream=True)
            response.raise_for_status()
            with open(FILENAME, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            st.success("Download complete! Loading app...")
        except Exception as e:
            st.error(f"Error downloading file: {e}")
            st.stop()

# -----------------------------------------------------------------------------
# 4. LOAD DATA & LOGIC (UNCHANGED)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

try:
    movies, similarity = load_data()
    movies_list = movies["title"].values
except FileNotFoundError:
    st.error("Model files not found. Please check the download script URL.")
    st.stop()

def fetch_poster(movie_id):
    API_KEY = "a4ca7366efe2e558aa8f2fffe23d3ca9"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return "https://via.placeholder.com/500x750?text=No+Poster" # Fallback image
    except:
        return "https://via.placeholder.com/500x750?text=Error"

def recommend(movie):
    try:
        movie_index = movies[movies["title"] == movie].index[0]
        distances = similarity[movie_index]
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

# -----------------------------------------------------------------------------
# 5. UI LAYOUT
# -----------------------------------------------------------------------------

# --- Header Section ---
st.markdown("<h1 class='main-header'> 🎬 MOVIE LENS</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-header'><i>Discover your next favorite movie with AI</i></p>", unsafe_allow_html=True)

# --- Search Section (Centered with spacing) ---
col1, col2, col3 = st.columns([1, 6, 1]) # Adjusted ratio for better mobile/desktop view

with col2:
    with st.container(border=True): # Adds a nice box around the search area
        selected_movie = st.selectbox(
            "Select a movie you love:",
            movies_list,
            index=None,
            placeholder="Start typing to search...",
        )
        
        st.write("") # Spacer
        
        # Centered Button
        b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
        with b_col2:
            recommend_button = st.button("Get Recommendations", type="primary", use_container_width=True)

# --- Results Section ---
if recommend_button:
    if selected_movie:
        # Add a subtle divider
        st.divider()
        
        with st.spinner(f"Analyzing cinematic patterns for '{selected_movie}'..."):
            names, posters = recommend(selected_movie)
        
        if names:
            st.subheader(f"Because you watched *{selected_movie}*:")
            st.write("") # Spacer

            # Dynamic Grid Layout
            cols = st.columns(5) # Creates 5 columns
            
            for idx, col in enumerate(cols):
                with col:
                    # Create a "Card" look using container with border
                    with st.container(border=True):
                        # Poster
                        if posters[idx]:
                            st.image(posters[idx], use_container_width=True)
                        
                        # Title (Centered and bold using CSS class defined above)
                        st.markdown(f"<div class='movie-title'>{names[idx]}</div>", unsafe_allow_html=True)
        else:
            st.error("Oops! We couldn't find recommendations for that specific movie. Try another popular title!")
    else:
        st.warning("⚠️ Please select a movie from the dropdown first.")

# --- Footer ---
st.markdown("")
st.markdown("")
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: grey;'>
        <small>Powered by TMDB API | Built with Streamlit & Python</small>
    </div>
    """, 
    unsafe_allow_html=True
)

