"""
Movie Recommender System - Training Script
This script processes the movie data and generates the .pkl files required for the application.
Run this script ONCE to create all necessary files.
"""

import pandas as pd
import numpy as np
import pickle
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer

print("=" * 60)
print("MOVIE RECOMMENDER SYSTEM - TRAINING SCRIPT")
print("=" * 60)
print("\nThis process will take around 2-3 minutes...")
print("\nStep 1: Loading datasets...")

# Load the datasets
movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

print(f"Loaded {len(movies)} movies")

# Merge the datasets
print("\nStep 2: Merging datasets...")
movies = movies.merge(credits, on="title")

# Select necessary columns
movies = movies[["id", "title", "overview", "genres", "keywords", "cast", "crew"]]
movies.columns = ["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]

# Drop rows where 'overview' is missing
movies = movies.dropna(subset=['overview'])

print(f"Merged datasets - {len(movies)} movies remaining")

# Function to convert JSON strings to list of names
def convert(obj):
    names = []
    try:
        for item in ast.literal_eval(obj):
            names.append(item["name"])
    except:
        pass
    return names

# Function to get the director's name
def fetch_director(obj):
    directors = []
    try:
        for item in ast.literal_eval(obj):
            if item["job"] == "Director":
                directors.append(item["name"])
                break
    except:
        pass
    return directors

# Function to get the top 3 cast members
def convert_cast(obj):
    cast_list = []
    count = 0
    try:
        for item in ast.literal_eval(obj):
            if count < 3:
                cast_list.append(item["name"])
                count += 1
            else:
                break
    except:
        pass
    return cast_list

print("\nStep 3: Processing genres, keywords, cast, and crew...")

# Apply conversions
movies["genres"] = movies["genres"].apply(convert)
movies["keywords"] = movies["keywords"].apply(convert)
movies["cast"] = movies["cast"].apply(convert_cast)
movies["crew"] = movies["crew"].apply(fetch_director)

print("Extracted features")

# Convert 'overview' from string to list of words
movies["overview"] = movies["overview"].apply(lambda x: x.split())

print("\nStep 4: Removing spaces from names...")

# Remove spaces from all lists
def remove_spaces(names):
    return [name.replace(" ", "") for name in names]

movies["genres"] = movies["genres"].apply(remove_spaces)
movies["keywords"] = movies["keywords"].apply(remove_spaces)
movies["cast"] = movies["cast"].apply(remove_spaces)
movies["crew"] = movies["crew"].apply(remove_spaces)

print("Cleaned data")

# Create a 'tags' column by combining all features
print("\nStep 5: Creating combined tags...")
movies["tags"] = movies["overview"] + movies["genres"] + movies["keywords"] + movies["cast"] + movies["crew"]

# Convert the 'tags' list into a string
movies["tags"] = movies["tags"].apply(lambda x: " ".join(x))

# Convert to lowercase
movies["tags"] = movies["tags"].apply(lambda x: x.lower())

print("Created tags")

# Apply stemming
print("\nStep 6: Applying stemming (this may take a minute)...")
ps = PorterStemmer()

def stem(text):
    return " ".join([ps.stem(word) for word in text.split()])

movies["tags"] = movies["tags"].apply(stem)

print("Stemming complete")

# Create a final dataframe with only the required columns
final_df = movies[["movie_id", "title", "tags"]].copy()

print("\nStep 7: Vectorizing text (creating feature matrix)...")

# Vectorization using CountVectorizer
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(final_df["tags"]).toarray()

print(f"Created vectors: {vectors.shape[0]} movies × {vectors.shape[1]} features")

# Calculate similarity matrix
print("\nStep 8: Calculating similarity matrix...")
print("This step might take some time...")

similarity = cosine_similarity(vectors)

print(f"Similarity matrix created: {similarity.shape[0]} × {similarity.shape[1]}")

# Save the generated files
print("\nStep 9: Saving .pkl files...")

pickle.dump(final_df, open("movies.pkl", "wb"))
print("Saved movies.pkl")

pickle.dump(similarity, open("similarity.pkl", "wb"))
print("Saved similarity.pkl")

print("=" * 60)
print("SUCCESS! All files generated!")
print("=" * 60)
print("\nGenerated files:")
print("movies.pkl")
print("similarity.pkl")
print("\nYou can now run your Streamlit app!")
print("Run: streamlit run app.py")
print("=" * 60)
