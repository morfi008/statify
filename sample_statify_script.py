# sample script

import api_client

# Initialize the Spotify API client
client = api_client.SpotifyAPI(api_client.client_id, api_client.client_secret)

# Example: Search for tracks
try:
    search_results = client.search("Time", search_type="track", limit=5)
    print("Search Results:")
    for track in search_results.get("tracks", {}).get("items", []):
        print(f"- {track['name']} by {track['artists'][0]['name']}")
    
    # Example: Search for an artist and get their popularity
    artist_results = client.search_artists("The Beatles", limit=1)
    if artist_results.get("artists", {}).get("items"):
        artist = artist_results["artists"]["items"][0]
        artist_id = artist["id"]
        print(f"\nArtist: {artist['name']}")
        
        # Get artist popularity
        popularity_data = client.get_artist_popularity(artist_id)
        print(f"Popularity: {popularity_data['popularity']}/100")
        print(f"Followers: {popularity_data['followers']:,}")
        
        # Calculate Potty Mouth Meter (this might take a while for artists with many albums)
        print("Calculating Potty Mouth Meter...")
        pmm_score = client.calculate_potty_mouth_meter(artist_id)
        print(f"Potty Mouth Meter: {pmm_score:.1f}% explicit tracks")
        
except Exception as e:
    print(f"Error: {e}")

