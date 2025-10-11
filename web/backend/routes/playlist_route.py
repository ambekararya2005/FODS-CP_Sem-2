"""
Playlist route for generating emotion-based playlists
Integrates with C++ playlist engine
"""

from flask import Blueprint, request, jsonify
import subprocess
import json
import os

playlist_bp = Blueprint('playlist', __name__)

# Path to C++ executable
CPP_EXECUTABLE = os.path.join(
    os.path.dirname(__file__), 
    '..', '..', '..', 'cpp', 'build', 'emotion_playlist.exe'
)

# Path to songs CSV
SONGS_CSV = os.path.join(
    os.path.dirname(__file__),
    '..', '..', '..', 'data', 'songs.csv'
)


def call_cpp_engine(emotions):
    """
    Call C++ playlist engine
    
    Args:
        emotions: List of emotion strings
        
    Returns:
        Dictionary with filtered songs
    """
    try:
        # Join emotions with comma
        emotions_str = ','.join(emotions)
        
        # Call C++ executable
        result = subprocess.run(
            [CPP_EXECUTABLE, SONGS_CSV, emotions_str],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise Exception(f"C++ engine error: {result.stderr}")
        
        # Parse JSON output
        playlist_data = json.loads(result.stdout)
        return playlist_data
        
    except subprocess.TimeoutExpired:
        raise Exception("C++ engine timeout")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse C++ output: {str(e)}")
    except FileNotFoundError:
        raise Exception(f"C++ executable not found at {CPP_EXECUTABLE}")
    except Exception as e:
        raise Exception(f"C++ engine error: {str(e)}")


@playlist_bp.route('/playlist', methods=['POST', 'OPTIONS'])
def generate_playlist():
    """
    Generate playlist based on emotions
    
    Request body:
        {
            "emotions": ["happy", "excited"]
        }
    
    Response:
        {
            "emotions": ["happy", "excited"],
            "songs": [
                {
                    "id": 1,
                    "title": "Happy Song",
                    "artist": "Artist Name",
                    "lyrics": "...",
                    "emotion": "happy"
                }
            ],
            "count": 1
        }
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Parse request
        data = request.get_json()
        
        if not data or 'emotions' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing required field: emotions'
            }), 400
        
        emotions = data['emotions']
        
        # Validate emotions
        if not isinstance(emotions, list) or len(emotions) == 0:
            return jsonify({
                'error': 'Bad Request',
                'message': 'emotions must be a non-empty list'
            }), 400
        
        # Validate each emotion is a string
        for emotion in emotions:
            if not isinstance(emotion, str) or not emotion.strip():
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'All emotions must be non-empty strings'
                }), 400
        
        # Call C++ engine
        playlist_data = call_cpp_engine(emotions)
        
        # Add emotions to response
        response = {
            'emotions': emotions,
            'songs': playlist_data['songs'],
            'count': playlist_data['count']
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in playlist endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@playlist_bp.route('/playlist/full', methods=['POST', 'OPTIONS'])
def generate_full_playlist():
    """
    Complete workflow: classify text and generate playlist
    
    Request body:
        {
            "text": "I feel so happy today!",
            "top_k": 3,
            "threshold": 0.1
        }
    
    Response:
        {
            "text": "I feel so happy today!",
            "classification": {
                "raw_emotions": [...],
                "simplified_emotions": ["happy"],
                "dominant_emotion": "joy",
                "confidence": 0.85
            },
            "playlist": {
                "emotions": ["happy"],
                "songs": [...],
                "count": 5
            }
        }
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Parse request
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing required field: text'
            }), 400
        
        text = data['text']
        top_k = data.get('top_k', 3)
        threshold = data.get('threshold', 0.1)
        
        # Import classifier
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ai'))
        from classify import EmotionClassifier
        
        # Initialize and classify
        from routes.classify_route import get_classifier
        classifier = get_classifier()
        classification = classifier.classify(text, top_k=top_k, threshold=threshold)
        
        # Get simplified emotions for playlist
        emotions = classification['simplified_emotions']
        
        if not emotions:
            emotions = ['neutral']
        
        # Generate playlist
        playlist_data = call_cpp_engine(emotions)
        
        # Combine results
        response = {
            'text': text,
            'classification': {
                'raw_emotions': classification['raw_emotions'],
                'simplified_emotions': classification['simplified_emotions'],
                'dominant_emotion': classification['dominant_emotion'],
                'confidence': classification['confidence']
            },
            'playlist': {
                'emotions': emotions,
                'songs': playlist_data['songs'],
                'count': playlist_data['count']
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in playlist/full endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
