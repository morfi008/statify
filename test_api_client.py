import unittest
from unittest.mock import Mock, patch, MagicMock
import datetime
import json
from api_client import SpotifyAPI


class TestSpotifyAPI(unittest.TestCase):
    
    def setUp(self):
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.api = SpotifyAPI(self.client_id, self.client_secret)
    
    def test_init(self):
        self.assertEqual(self.api.client_id, self.client_id)
        self.assertEqual(self.api.client_secret, self.client_secret)
        self.assertIsNone(self.api.access_token)
        self.assertTrue(self.api.access_token_did_expire)
    
    def test_get_client_creds(self):
        expected = "dGVzdF9jbGllbnRfaWQ6dGVzdF9jbGllbnRfc2VjcmV0"  # base64 of "test_client_id:test_client_secret"
        result = self.api.get_client_creds()
        self.assertEqual(result, expected)
    
    def test_get_client_creds_missing_credentials(self):
        api = SpotifyAPI(None, None)
        with self.assertRaises(Exception) as context:
            api.get_client_creds()
        self.assertIn("You must set client_id and client_secret", str(context.exception))
    
    def test_get_token_headers(self):
        headers = self.api.get_token_headers()
        self.assertIn("Authorization", headers)
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/x-www-form-urlencoded")
        self.assertTrue(headers["Authorization"].startswith("Basic "))
    
    def test_get_token_data(self):
        data = self.api.get_token_data()
        self.assertEqual(data["grant_type"], "client_credentials")
    
    @patch('api_client.requests.post')
    def test_perform_auth_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response
        
        result = self.api.perform_auth()
        
        self.assertTrue(result)
        self.assertEqual(self.api.access_token, "test_token")
        self.assertFalse(self.api.access_token_did_expire)
        mock_post.assert_called_once()
    
    @patch('api_client.requests.post')
    def test_perform_auth_failure(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.api.perform_auth()
        self.assertIn("Could not authenticate client", str(context.exception))
    
    def test_get_access_token_none(self):
        self.api.access_token = None
        
        def mock_perform_auth():
            self.api.access_token = "test_token"
            self.api.access_token_expires = datetime.datetime.now() + datetime.timedelta(hours=1)
            self.api.access_token_did_expire = False
            return True
        
        with patch.object(self.api, 'perform_auth', side_effect=mock_perform_auth) as mock_auth:
            token = self.api.get_access_token()
            
            self.assertEqual(token, "test_token")
            mock_auth.assert_called_once()
    
    def test_get_access_token_expired(self):
        self.api.access_token = "expired_token"
        self.api.access_token_expires = datetime.datetime.now() - datetime.timedelta(hours=1)
        
        def mock_perform_auth():
            self.api.access_token = "new_token"
            self.api.access_token_expires = datetime.datetime.now() + datetime.timedelta(hours=1)
            self.api.access_token_did_expire = False
            return True
        
        with patch.object(self.api, 'perform_auth', side_effect=mock_perform_auth) as mock_auth:
            token = self.api.get_access_token()
            
            self.assertEqual(token, "new_token")
            mock_auth.assert_called_once()
    
    def test_get_resource_header(self):
        with patch.object(self.api, 'get_access_token', return_value="test_token"):
            headers = self.api.get_resource_header()
            
            self.assertIn("Authorization", headers)
            self.assertEqual(headers["Authorization"], "Bearer test_token")
    
    @patch('api_client.requests.get')
    def test_get_resource_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_id", "name": "Test Artist"}
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            result = self.api.get_resource("test_id", "artists")
            
            self.assertEqual(result["id"], "test_id")
            self.assertEqual(result["name"], "Test Artist")
            mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_get_resource_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            result = self.api.get_resource("invalid_id", "artists")
            
            self.assertEqual(result, {})
    
    def test_get_track(self):
        with patch.object(self.api, 'get_resource', return_value={"id": "track_id"}) as mock_get_resource:
            result = self.api.get_track("track_id")
            
            mock_get_resource.assert_called_once_with("track_id", resource_type="tracks")
            self.assertEqual(result["id"], "track_id")
    
    def test_get_album(self):
        with patch.object(self.api, 'get_resource', return_value={"id": "album_id"}) as mock_get_resource:
            result = self.api.get_album("album_id")
            
            mock_get_resource.assert_called_once_with("album_id", resource_type="albums")
            self.assertEqual(result["id"], "album_id")
    
    def test_get_artist(self):
        with patch.object(self.api, 'get_resource', return_value={"id": "artist_id"}) as mock_get_resource:
            result = self.api.get_artist("artist_id")
            
            mock_get_resource.assert_called_once_with("artist_id", resource_type="artists")
            self.assertEqual(result["id"], "artist_id")
    
    @patch('api_client.requests.get')
    def test_search_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tracks": {
                "items": [{"name": "Test Track", "id": "track_id"}]
            }
        }
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            result = self.api.search("test query", "track", 10, 0, "US")
            
            self.assertIn("tracks", result)
            self.assertEqual(len(result["tracks"]["items"]), 1)
            mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_search_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            with self.assertRaises(Exception) as context:
                self.api.search("test query")
            
            self.assertIn("Search failed with status 400", str(context.exception))
    
    def test_search_artists(self):
        with patch.object(self.api, 'search', return_value={"artists": {"items": []}}) as mock_search:
            result = self.api.search_artists("test artist", 5, 10, "US")
            
            mock_search.assert_called_once_with("test artist", "artist", 5, 10, "US")
    
    def test_search_albums(self):
        with patch.object(self.api, 'search', return_value={"albums": {"items": []}}) as mock_search:
            result = self.api.search_albums("test album", 5, 10, "US")
            
            mock_search.assert_called_once_with("test album", "album", 5, 10, "US")
    
    def test_search_tracks(self):
        with patch.object(self.api, 'search', return_value={"tracks": {"items": []}}) as mock_search:
            result = self.api.search_tracks("test track", 5, 10, "US")
            
            mock_search.assert_called_once_with("test track", "track", 5, 10, "US")
    
    @patch('api_client.requests.get')
    def test_get_albums_by_artist_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"id": "album1", "name": "Album 1"}]
        }
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            result = self.api.get_albums_by_artist("artist_id", "album", "US", 10, 0)
            
            self.assertIn("items", result)
            self.assertEqual(len(result["items"]), 1)
            mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_get_albums_by_artist_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            with self.assertRaises(Exception) as context:
                self.api.get_albums_by_artist("invalid_artist_id")
            
            self.assertIn("Failed to get albums for artist", str(context.exception))
    
    @patch('api_client.requests.get')
    def test_get_album_tracks_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"id": "track1", "name": "Track 1"}]
        }
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            result = self.api.get_album_tracks("album_id", "US", 10, 0)
            
            self.assertIn("items", result)
            self.assertEqual(len(result["items"]), 1)
            mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_get_album_tracks_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            with self.assertRaises(Exception) as context:
                self.api.get_album_tracks("invalid_album_id")
            
            self.assertIn("Failed to get tracks for album", str(context.exception))
    
    def test_get_all_tracks_by_artist(self):
        albums_response = {
            "items": [
                {"id": "album1", "name": "Album 1"},
                {"id": "album2", "name": "Album 2"}
            ]
        }
        tracks_response = {
            "items": [
                {"id": "track1", "name": "Track 1"},
                {"id": "track2", "name": "Track 2"}
            ]
        }
        
        with patch.object(self.api, 'get_albums_by_artist', return_value=albums_response) as mock_albums, \
             patch.object(self.api, 'get_album_tracks', return_value=tracks_response) as mock_tracks:
            
            result = self.api.get_all_tracks_by_artist("artist_id")
            
            self.assertEqual(len(result), 4)  # 2 albums * 2 tracks each
            mock_albums.assert_called_once()
            self.assertEqual(mock_tracks.call_count, 2)
    
    @patch('api_client.requests.get')
    def test_get_multiple_tracks_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tracks": [
                {"id": "track1", "name": "Track 1"},
                {"id": "track2", "name": "Track 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            result = self.api.get_multiple_tracks(["track1", "track2"], "US")
            
            self.assertIn("tracks", result)
            self.assertEqual(len(result["tracks"]), 2)
            mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_get_multiple_tracks_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            with self.assertRaises(Exception) as context:
                self.api.get_multiple_tracks(["invalid_track_id"])
            
            self.assertIn("Failed to get multiple tracks", str(context.exception))
    
    @patch('api_client.requests.get')
    def test_get_artist_top_tracks_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tracks": [{"id": "top_track1", "name": "Top Track 1"}]
        }
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            result = self.api.get_artist_top_tracks("artist_id", "US")
            
            self.assertIn("tracks", result)
            self.assertEqual(len(result["tracks"]), 1)
            mock_get.assert_called_once()
    
    @patch('api_client.requests.get')
    def test_get_artist_top_tracks_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with patch.object(self.api, 'get_resource_header', return_value={"Authorization": "Bearer test_token"}):
            with self.assertRaises(Exception) as context:
                self.api.get_artist_top_tracks("invalid_artist_id")
            
            self.assertIn("Failed to get top tracks for artist", str(context.exception))
    
    def test_calculate_potty_mouth_meter(self):
        tracks = [
            {"explicit": True, "name": "Track 1"},
            {"explicit": False, "name": "Track 2"},
            {"explicit": True, "name": "Track 3"},
            {"explicit": False, "name": "Track 4"}
        ]
        
        with patch.object(self.api, 'get_all_tracks_by_artist', return_value=tracks):
            result = self.api.calculate_potty_mouth_meter("artist_id")
            
            self.assertEqual(result, 50.0)  # 2 explicit out of 4 tracks = 50%
    
    def test_calculate_potty_mouth_meter_no_tracks(self):
        with patch.object(self.api, 'get_all_tracks_by_artist', return_value=[]):
            result = self.api.calculate_potty_mouth_meter("artist_id")
            
            self.assertEqual(result, 0.0)
    
    def test_calculate_potty_mouth_meter_all_explicit(self):
        tracks = [
            {"explicit": True, "name": "Track 1"},
            {"explicit": True, "name": "Track 2"}
        ]
        
        with patch.object(self.api, 'get_all_tracks_by_artist', return_value=tracks):
            result = self.api.calculate_potty_mouth_meter("artist_id")
            
            self.assertEqual(result, 100.0)
    
    def test_get_artist_popularity(self):
        artist_data = {
            "popularity": 85,
            "followers": {"total": 1000000}
        }
        
        with patch.object(self.api, 'get_artist', return_value=artist_data):
            result = self.api.get_artist_popularity("artist_id")
            
            self.assertEqual(result["popularity"], 85)
            self.assertEqual(result["followers"], 1000000)
    
    def test_get_artist_popularity_missing_data(self):
        artist_data = {}
        
        with patch.object(self.api, 'get_artist', return_value=artist_data):
            result = self.api.get_artist_popularity("artist_id")
            
            self.assertEqual(result["popularity"], 0)
            self.assertEqual(result["followers"], 0)


if __name__ == '__main__':
    unittest.main()