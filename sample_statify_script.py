# sample script

import api_client

c = api_client.SpotifyAPI(api_client.client_id, api_client.client_secret)

c._search_("Time", search_type="track")

