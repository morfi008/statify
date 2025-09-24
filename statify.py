# STATIFY CLASSES

class potty_mouth_meter(object):
    """
    Calculates the Potty Mouth Meter (PMM) for an artist.
    PMM is the percentage of explicit tracks in an artist's discography.
    """
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.artist_id = None
        self.artist_pmm_score = None
    
    def calculate_pmm(self, artist_id):
        """Calculate the Potty Mouth Meter score for an artist."""
        self.artist_id = artist_id
        tracks = self.api_client.get_all_tracks_by_artist(artist_id)
        
        if not tracks:
            self.artist_pmm_score = 0.0
            return self.artist_pmm_score
            
        explicit_count = sum(1 for track in tracks if track.get("explicit", False))
        total_count = len(tracks)
        
        self.artist_pmm_score = (explicit_count / total_count) * 100 if total_count > 0 else 0.0
        return self.artist_pmm_score


class mom_i_made_it_meter(object):
    """
    Calculates the Mom I Made It Meter (MIMIM) for an artist.
    MIMIM combines popularity score and follower count to measure mainstream success.
    """
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.artist_id = None
        self.artist_mimim_score = None
        self.popularity_rating = None
        self.followers_count = None
    
    def calculate_mimim(self, artist_id):
        """Calculate the Mom I Made It Meter score for an artist."""
        self.artist_id = artist_id
        artist_data = self.api_client.get_artist(artist_id)
        
        self.popularity_rating = artist_data.get("popularity", 0)
        self.followers_count = artist_data.get("followers", {}).get("total", 0)
        
        # Calculate MIMIM score as a weighted combination of popularity and followers
        # Normalize followers to a 0-100 scale (assuming 10M followers = 100)
        normalized_followers = min((self.followers_count / 10000000) * 100, 100)
        
        # Weight: 60% popularity, 40% followers
        self.artist_mimim_score = (self.popularity_rating * 0.6) + (normalized_followers * 0.4)
        
        return {
            "mimim_score": round(self.artist_mimim_score, 2),
            "popularity": self.popularity_rating,
            "followers": self.followers_count
        }


class bff_picker(object):
    """
    Finds the BFF (Best Friend Forever) for an artist.
    BFF is the most frequently collaborating artist based on track features.
    """
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.artist_id = None
        self.artist_bff = None
        self.collaborator_counts = {}
    
    def find_bff(self, artist_id):
        """Find the most frequent collaborating artist."""
        self.artist_id = artist_id
        tracks = self.api_client.get_all_tracks_by_artist(artist_id)
        
        if not tracks:
            self.artist_bff = None
            return None
        
        # Count collaborators from track artists
        for track in tracks:
            artists = track.get("artists", [])
            # Skip if only one artist (no collaboration)
            if len(artists) <= 1:
                continue
                
            for artist in artists:
                collaborator_id = artist.get("id")
                collaborator_name = artist.get("name")
                
                # Skip the main artist
                if collaborator_id == artist_id:
                    continue
                    
                if collaborator_id not in self.collaborator_counts:
                    self.collaborator_counts[collaborator_id] = {
                        "name": collaborator_name,
                        "count": 0
                    }
                self.collaborator_counts[collaborator_id]["count"] += 1
        
        if not self.collaborator_counts:
            self.artist_bff = None
            return None
        
        # Find the most frequent collaborator
        bff_id = max(self.collaborator_counts.keys(), 
                    key=lambda x: self.collaborator_counts[x]["count"])
        
        self.artist_bff = {
            "id": bff_id,
            "name": self.collaborator_counts[bff_id]["name"],
            "collaboration_count": self.collaborator_counts[bff_id]["count"]
        }
        
        return self.artist_bff

