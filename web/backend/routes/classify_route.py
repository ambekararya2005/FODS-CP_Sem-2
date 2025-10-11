"""
Emotion classification route
Handles text emotion analysis using the AI classifier
"""

from flask import Blueprint, request, jsonify
import os
import sys

classify_bp = Blueprint('classify', __name__)

# Global classifier instance for caching
_classifier = None

def get_classifier():
    """Get or create classifier instance (singleton pattern)"""
    global _classifier
    if _classifier is None:
        # Add AI directory to path
        ai_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ai')
        sys.path.append(ai_path)
        
        from classify import EmotionClassifier
        _classifier = EmotionClassifier()
    
    return _classifier


@classify_bp.route('/classify', methods=['POST', 'OPTIONS'])
def classify_emotion():
    """
    Classify emotions in text
    
    Request body:
        {
            "text": "I feel so happy today!",
            "top_k": 3,
            "threshold": 0.1
        }
    
    Response:
        {
            "text": "I feel so happy today!",
            "raw_emotions": [...],
            "simplified_emotions": ["happy"],
            "dominant_emotion": "joy",
            "confidence": 0.85
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
        
        # Validate text
        if not isinstance(text, str) or not text.strip():
            return jsonify({
                'error': 'Bad Request',
                'message': 'text must be a non-empty string'
            }), 400
        
        # Get classifier and classify
        classifier = get_classifier()
        result = classifier.classify(text, top_k=top_k, threshold=threshold)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in classify endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@classify_bp.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze_emotion():
    """
    Complete emotion analysis with simplified response for frontend
    
    Request body:
        {
            "text": "I feel so happy today!"
        }
    
    Response:
        {
            "emotion": "happy",
            "confidence": 0.85,
            "playlist": [...]
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
        
        # Validate text
        if not isinstance(text, str) or not text.strip():
            return jsonify({
                'error': 'Bad Request',
                'message': 'text must be a non-empty string'
            }), 400
        
        # Get classifier and classify
        classifier = get_classifier()
        result = classifier.classify(text, top_k=3, threshold=0.1)
        
        # Get simplified emotions for playlist
        emotions = result['simplified_emotions']
        if not emotions:
            emotions = ['neutral']
        
        # Import playlist route to generate playlist
        from routes.playlist_route import call_cpp_engine
        playlist_data = call_cpp_engine(emotions)
        
        # Format response for frontend
        response = {
            'emotion': result['dominant_emotion'],
            'confidence': result['confidence'],
            'playlist': playlist_data['songs']
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
