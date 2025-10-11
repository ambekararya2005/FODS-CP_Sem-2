#!/usr/bin/env python3
"""
Flask backend for Emotion Playlist
Provides REST API for emotion classification and playlist generation
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from routes.classify_route import classify_bp
from routes.playlist_route import playlist_bp

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Register blueprints
app.register_blueprint(classify_bp, url_prefix='/api')
app.register_blueprint(playlist_bp, url_prefix='/api')


@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'name': 'Emotion Playlist API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'classify': '/api/classify',
            'playlist': '/api/playlist',
            'health': '/api/health'
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("=" * 60)
    print("Emotion Playlist API Server")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"CORS Origins: http://localhost:5173, http://localhost:3000")
    print("=" * 60)
    print("\nStarting server...\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )