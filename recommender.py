from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

def get_genre_list():
    """Fetch and return the list of genres from TMDb."""
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get('genres', [])

def display_genre_list(genres):
    """Display the list of genres to the user."""
    print("Available Genres:")
    for genre in genres:
        print(f"ID: {genre['id']}, Name: {genre['name']}")

def fetch_movies(genre_id, start_year, end_year, page=1):
    """Fetch movies based on genre ID and release year range, with optional pagination."""
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}&primary_release_date.gte={start_year}-01-01&primary_release_date.lte={end_year}-12-31&page={page}"
    response = requests.get(url)
    data = response.json()

    if 'results' in data:
        return data['results']
    else:
        print("Error fetching data from TMDb:", data)
        return []

def get_imdb_rating(imdb_id):
    """Fetch IMDb rating using OMDb API."""
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    rating = data.get('imdbRating', 'N/A')
    return rating if rating != 'N/A' else None

def get_movie_ratings(movie_id):
    """Fetch ratings for a movie."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids"
    response = requests.get(url)
    data = response.json()

    imdb_id = data.get('external_ids', {}).get('imdb_id', '')
    imdb_rating = None

    if imdb_id:
        imdb_rating = get_imdb_rating(imdb_id)

    return {
        'IMDb': imdb_rating
        # Add logic for other sites if needed
    }

def recommend_movies(genre_id, start_year, end_year, page=1):
    """Recommend movies based on genre ID and release year range."""
    movies = fetch_movies(genre_id, start_year, end_year, page)
    if not movies:
        print("No movies found matching your criteria.")
        return []

    movie_list = []
    for movie in movies:
        movie_id = movie['id']
        movie_data = {
            'title': movie['title'],
            'year': movie['release_date'][:4],
            'ratings': get_movie_ratings(movie_id)
        }
        movie_list.append(movie_data)

    # Sort by IMDb rating if available and return top 3
    def rating_to_float(rating):
        try:
            return float(rating)
        except (ValueError, TypeError):
            return 0

    sorted_movies = sorted(movie_list, key=lambda x: rating_to_float(x['ratings'].get('IMDb')), reverse=True)
    return sorted_movies[:3]

def display_recommendations(recommendations):
    """Display the top movie recommendations."""
    print("\nTop movie recommendations:")
    for i, movie in enumerate(recommendations, start=1):
        print(f"{i}. {movie['title']} ({movie['year']}) - Ratings: {movie['ratings']}")

def main():
    genres = get_genre_list()
    display_genre_list(genres)

    try:
        genre_id = int(input("\nEnter the genre ID you want: ").strip())
        start_year = input("Enter start year: ").strip()
        end_year = input("Enter end year: ").strip()
    except ValueError:
        print("Invalid input. Please enter a number for the genre ID and valid years.")
        return

    page = 1
    recommendations = recommend_movies(genre_id, start_year, end_year, page)
    all_movie_titles = set(movie['title'] for movie in recommendations)

    if recommendations:
        while True:
            display_recommendations(recommendations)
            print("\nOptions:")
            print("1. Show more movies")
            print("2. Go back")
            choice = input("Enter your choice: ").strip()

            if choice == "1":
                page += 1
                more_movies = fetch_movies(genre_id, start_year, end_year, page)
                if more_movies:
                    # Exclude already shown movies
                    additional_movies = [movie for movie in more_movies if movie['title'] not in all_movie_titles]
                    
                    if additional_movies:
                        # Prepare new recommendations list
                        additional_movie_list = []
                        for movie in additional_movies[:3]:
                            movie_id = movie['id']
                            movie_data = {
                                'title': movie['title'],
                                'year': movie['release_date'][:4],
                                'ratings': get_movie_ratings(movie_id)
                            }
                            additional_movie_list.append(movie_data)

                        if additional_movie_list:
                            print("\nAdditional movie recommendations:")
                            display_recommendations(additional_movie_list)
                            # Update recommendations with the new movies
                            recommendations = additional_movie_list
                            all_movie_titles.update(movie['title'] for movie in additional_movie_list)
                        else:
                            print("No more new movies found.")
                    else:
                        print("No new movies found.")
                else:
                    print("No more movies found.")
            elif choice == "2":
                break
            else:
                print("Invalid choice, please try again.")
    else:
        print("No movies found matching your criteria.")

main()
