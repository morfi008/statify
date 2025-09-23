# Statify

Statify is a Python application that analyzes Spotify artists using the Spotify Web API. Learn more about your favorite artists by accessing their comprehensive data from Spotify.

## Features

The project calculates three key metrics for any given artist:

1. **Potty Mouth Meter (PMM)**: Percentage of explicit tracks in an artist's discography
2. **Mom I Made It Meter (MIMIM)**: Artist popularity metrics including followers and popularity score
3. **BFF Picker**: Identifies the most frequent collaborating artists

## Architecture

### Core Components

- **`api_client.py`**: Contains the `SpotifyAPI` class that handles all Spotify Web API interactions including authentication, token management, and data retrieval
- **`statify.py`**: Defines the main analysis classes (`potty_mouth_meter`, `mom_i_made_it_meter`, `bff_picker`) - currently contains class stubs
- **`secrets.py`**: Stores Spotify API credentials (client_id and client_secret)
- **`sample_statify_script.py`**: Example usage script demonstrating API client initialization and search functionality

### API Client Features

The `SpotifyAPI` class provides:
- **Authentication**: OAuth client credentials flow with automatic token refresh
- **Resource Access**: Generic API calls for artists, albums, and tracks
- **Search Functionality**: Query Spotify's search endpoint for artists, albums, and tracks
- **Analysis Methods**: Custom methods for gathering comprehensive album/track data for metric calculations

## Installation

### Dependencies

The project uses standard Python libraries:
- `requests` - HTTP requests to Spotify API
- `base64` - Credential encoding for authentication
- `datetime` - Token expiration handling
- `urllib.parse` - URL encoding for search queries
- `json` - API response parsing

### Setup

1. Obtain Spotify API credentials from the [Spotify Developer Dashboard](https://developer.spotify.com/)
2. Add your credentials to `secrets.py`:
   ```python
   client_id = "your_client_id_here"
   client_secret = "your_client_secret_here"
   ```

## Usage

### Basic Usage
```bash
python sample_statify_script.py
```

### API Client Usage
```python
import api_client
client = api_client.SpotifyAPI(api_client.client_id, api_client.client_secret)

# Search for artists
results = client.search_artists("Taylor Swift")

# Get artist information
artist_data = client.get_artist("artist_id")

# Calculate metrics
pmm_score = client.calculate_potty_mouth_meter("artist_id")
popularity = client.get_artist_popularity("artist_id")
```

## Testing

The project includes comprehensive unit tests for the API client functionality.

### Running Tests

To run the test suite:

```bash
python test_api_client.py
```

Or using the unittest module:

```bash
python -m unittest test_api_client.py
```

### Test Coverage

The test suite covers:
- Authentication and token management
- API resource retrieval (artists, albums, tracks)
- Search functionality
- Error handling and edge cases
- Metric calculation methods
- All major SpotifyAPI class methods

## Development Status

The project is currently in early development:
- ✅ Core API client is functional and tested
- ✅ Authentication and data retrieval working
- ⚠️ Analysis classes are defined but not fully implemented
- ⚠️ Some methods may have syntax errors that need addressing

## Security Notes

- API credentials are currently stored in `secrets.py`
- **Important**: Keep your `secrets.py` file private and do not commit actual credentials to version control
- Consider using environment variables for production deployments

## Acknowledgments

Thanks to CodingEntrepreneurs on YouTube for the tutorial on using the Spotify API: https://youtu.be/xdq6Gz33khQ