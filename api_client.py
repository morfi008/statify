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
            "Authorization": f"Basic {client_creds_b64}"
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

    def _search_(self, query_params):
        headers = self.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"
        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200,299):
            print(r.status_code)
            return {}
        print(r.status_code)
        print(r.text)
        return (r.text)

    def base_search(self, query=None):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = ""
        query_params = urlencode ({"q":query_params, "type":search_type.lower()})
        return self.base_search(query_params)
    


    # Statify operations : PMM, MIMD, BFF
    # For PMM: get explicit label for every song by artist, calculate %
    # For BFF: get collaborative artists on every song, find mode
    # For MIMD: get popularity score for artist

    def get_albums_by_artist(self, artist_id):
        endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        headers = self.get_resource_header()
        album_id_list = []
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        r = r.json()
        for i in r["items"]:
            album_id = i.get("id")
            album_id_list.append(album_id)
        return album_id_list

    def get_songs_on_album(self, album_id):
        endpoint = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        headers = self.get_resource_header()
        song_id_list = []
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        r = r.json()
        for i in r["items"]:
            song_id = i.get("id")
            song_id_list.append(song_id)
        return song_id_list

##    def get_all_songs_by_artist(self, artist_id):
##        albums = self.get_albums_by_artist(artist_id)
##        album_id_list = []
##        tracks_id_list = []
##        for i in album_id_list:
##            tracks = self.get_songs_on_album(album_id)
##        return album_id_list
##        # return json data for all songs on all albums artist

