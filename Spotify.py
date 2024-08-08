import os
import requests
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from dotenv import load_dotenv

load_dotenv()

# Load Spotify credentials from environment variables
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')

scope = "playlist-modify-public"

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=scope))

def get_jams_from_item_shop():
    url = "https://fortnite-api.com/v2/shop"
    result = {
        "hash": "",
        "tracks": []
    }
    with requests.session() as s:
        response = s.get(url)
        data = response.json()
    if data["status"] == 200:
        result["hash"] = data["data"]["hash"]
        seen_titles = set()
        for item in data["data"]["entries"]:
            if item["tracks"]:
                for track in item["tracks"]:
                    if track["title"] not in seen_titles:
                        result["tracks"].append({
                            "title": track["title"],
                            "artist": track["artist"],
                            "album": track["album"],
                            "releaseYear": track["releaseYear"]
                        })
                        seen_titles.add(track["title"])
    return result

def search_and_replace_tracks_in_playlist(playlist_id, tracks):
    track_ids = []
    for track in tracks:
        query = f"{track['artist']} {track['title']} {track.get('album', '')} {track.get('releaseYear', '')}"
        search_results = sp.search(q=query, type='track', limit=1)
        if search_results['tracks']['items']:
            track_id = search_results['tracks']['items'][0]['id']
            track_ids.append(track_id)
            print(f"Added {track['title']} by {track['artist']} to the playlist.")
        else:
            print(f"Could not find {track['title']} by {track['artist']} on Spotify.")
    
    # Replace tracks in the playlist in chunks of 100
    if track_ids:
        sp.playlist_replace_items(playlist_id, track_ids[:100])
        for i in range(100, len(track_ids), 100):
            sp.playlist_add_items(playlist_id, track_ids[i:i + 100])

if __name__ == "__main__":
    tracks = get_jams_from_item_shop()
    search_and_replace_tracks_in_playlist(PLAYLIST_ID, tracks["tracks"])
    print("Finished replacing tracks in the playlist.")