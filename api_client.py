#-----------------------------------------------------------------#
import json
import base64
import datetime
import requests
from urllib.parse import urlencode
from secrets import client_id
from secrets import client_secret



class SpotifyAPI(object):
    # client default configs
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    method = "POST"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    # API AUTHENTICATION FUNCTIONS
    
    def get_token_headers(self):
        client_creds_b64 = self.get_client_creds()
        return {
            "Authorization": f"Basic {client_creds_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def get_client_creds(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        # Get secrets
        client_creds = f"{client_id}:{client_secret}"
        # Encode secrets
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_data(self):
        return {
            "grant_type" : "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        # Make request for access token
        r = requests.post(token_url, data=token_data, headers=token_headers)
        # Check for validity
        valid_request = r.status_code in range(200, 299)
        if not valid_request:
            raise Exception("Could not authenticate client")
        # Handle successful authentication
        data = r.json()
        access_token = data['access_token']
        # expiration logic
        now = datetime.datetime.now()
        expires_in = data['expires_in'] #seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if self.access_token == None:
            self.perform_auth()
            return self.get_access_token()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        return token

    # ENTITY ACCESS FUNCTIONS
    
    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers
    
    def get_resource(self, lookup_id, resource_type='artists', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()

    def get_track(self, _id):
        return self.get_resource(_id, resource_type='tracks')

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    def search(self, query, search_type="track", limit=20, offset=0, market=None):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        
        params = {
            "q": query,
            "type": search_type,
            "limit": limit,
            "offset": offset
        }
        
        if market:
            params["market"] = market
            
        r = requests.get(endpoint, headers=headers, params=params)
        if r.status_code not in range(200, 299):
            raise Exception(f"Search failed with status {r.status_code}: {r.text}")
        return r.json()

    def search_artists(self, query, limit=20, offset=0, market=None):
        return self.search(query, "artist", limit, offset, market)
    
    def search_albums(self, query, limit=20, offset=0, market=None):
        return self.search(query, "album", limit, offset, market)
    
    def search_tracks(self, query, limit=20, offset=0, market=None):
        return self.search(query, "track", limit, offset, market)
    


    # Statify operations : PMM, MIMD, BFF
    # For PMM: get explicit label for every song by artist
    # For BFF: get collaborative artists on every song
    # For MIMD: get popularity score for artist

    def get_albums_by_artist(self, artist_id, include_groups=None, market=None, limit=20, offset=0):
        endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        headers = self.get_resource_header()
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if include_groups:
            params["include_groups"] = include_groups
        if market:
            params["market"] = market
            
        r = requests.get(endpoint, headers=headers, params=params)
        if r.status_code not in range(200, 299):
            raise Exception(f"Failed to get albums for artist {artist_id}: {r.status_code}")
        return r.json()

    def get_album_tracks(self, album_id, market=None, limit=20, offset=0):
        endpoint = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        headers = self.get_resource_header()
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if market:
            params["market"] = market
            
        r = requests.get(endpoint, headers=headers, params=params)
        if r.status_code not in range(200, 299):
            raise Exception(f"Failed to get tracks for album {album_id}: {r.status_code}")
        return r.json()

    def get_all_tracks_by_artist(self, artist_id, include_groups="album,single", market=None):
        all_tracks = []
        offset = 0
        limit = 50
        
        while True:
            albums_response = self.get_albums_by_artist(
                artist_id, include_groups=include_groups, market=market, 
                limit=limit, offset=offset
            )
            
            albums = albums_response.get("items", [])
            if not albums:
                break
                
            for album in albums:
                album_id = album.get("id")
                if album_id:
                    tracks_response = self.get_album_tracks(album_id, market=market)
                    tracks = tracks_response.get("items", [])
                    all_tracks.extend(tracks)
            
            if len(albums) < limit:
                break
            offset += limit
            
        return all_tracks
    
    def get_multiple_tracks(self, track_ids, market=None):
        endpoint = "https://api.spotify.com/v1/tracks"
        headers = self.get_resource_header()
        
        params = {"ids": ",".join(track_ids)}
        if market:
            params["market"] = market
            
        r = requests.get(endpoint, headers=headers, params=params)
        if r.status_code not in range(200, 299):
            raise Exception(f"Failed to get multiple tracks: {r.status_code}")
        return r.json()
    
    def get_artist_top_tracks(self, artist_id, market="US"):
        endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
        headers = self.get_resource_header()
        
        params = {"market": market}
        
        r = requests.get(endpoint, headers=headers, params=params)
        if r.status_code not in range(200, 299):
            raise Exception(f"Failed to get top tracks for artist {artist_id}: {r.status_code}")
        return r.json()
    

