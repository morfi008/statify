import api_client
import secrets
import statify

# Create an instance of the SpotifyAPI client
spotify_client = api_client.SpotifyAPI(secrets.client_id, secrets.client_secret)

# Get user input
user_input_artist = input(f"Name an artist: ")

# Search for the artist and get the first result
search_results = spotify_client.search_artists(query=user_input_artist, limit=1)
artists = search_results.get("artists", {}).get("items", [])

if not artists:
    print(f"No artist found for '{user_input_artist}'")
    exit()

artist = artists[0]
artist_id = artist["id"]
artist_name = artist["name"]

print(f"Found artist: {artist_name}")

# Create instances of the Statify metric classes
pmm = statify.potty_mouth_meter(spotify_client)
mimim = statify.mom_i_made_it_meter(spotify_client)
bff = statify.bff_picker(spotify_client)

# Calculate the metrics
PMM_score = pmm.calculate_pmm(artist_id)
MIMIM_score = mimim.calculate_mimim(artist_id)
BFF_result = bff.find_bff(artist_id)

# Display results
print(f"""
{artist_name}'s Statify Profile:

    Potty Mouth Meter: {PMM_score:.1f}%
    Mom-I-Made-It Score: {MIMIM_score['mimim_score']}/100 (Popularity: {MIMIM_score['popularity']}, Followers: {MIMIM_score['followers']:,})
    BFF: {BFF_result['name'] if BFF_result else 'No collaborations found'} {f"({BFF_result['collaboration_count']} collaborations)" if BFF_result else ''}
""")