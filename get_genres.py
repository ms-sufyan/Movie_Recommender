from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

TMDB_API_KEY = os.getenv('TMDB_API_KEY')

def get_genres():
    if not TMDB_API_KEY:
        print("Error: TMDB_API_KEY is not set.")
        return

    try:
        genre_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
        response = requests.get(genre_url)
        data = response.json()

        # Print the full response for debugging
        print("API Response:", data)

        # Check for 'genres' key
        if 'genres' in data:
            print("Available Genres:")
            for genre in data['genres']:
                print(f"ID: {genre['id']}, Name: {genre['name']}")
        else:
            print("No 'genres' key found in response.")
    except Exception as e:
        print(f"Error fetching genres from TMDb: {e}")

def main():
    get_genres()

if __name__ == "__main__":
    main()
