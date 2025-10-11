# Emotion Playlist Project Design Documentation

## Overview
The Emotion Playlist project aims to create a music playlist application that curates songs based on the emotional content of lyrics. The application leverages machine learning to classify emotions from song lyrics and generate playlists that match the user's emotional state.

## Architecture
The project is structured into several components:

1. **Data Layer**: 
   - Contains song metadata and example lyrics.
   - `data/songs.csv`: A seed database for songs, including titles, artists, and genres.
   - `data/sample_lyrics.txt`: Example lyrics for testing and demonstration.

2. **C++ Backend**:
   - Implements core functionalities for playlist management.
   - `cpp/src/main.cpp`: Entry point for the command-line interface (CLI).
   - `cpp/src/playlist.h` and `cpp/src/playlist.cpp`: Define and implement the Playlist class, managing song collections.

3. **AI Component**:
   - Responsible for emotion classification based on lyrics.
   - `ai/classify.py`: Implements the emotion classifier.
   - `ai/train.py`: Fine-tunes the classifier model on a dataset.

4. **Web Interface**:
   - Provides a user-friendly interface for interaction.
   - `web/frontend`: Contains the React application for the frontend.
   - `web/backend`: Implements a Flask API for backend services.

## Design Decisions
- **Emotion Classification**: The choice of using machine learning for emotion classification allows for dynamic and accurate playlist generation based on user input.
- **C++ for Performance**: The backend is implemented in C++ for performance reasons, especially in handling large datasets and complex algorithms.
- **Separation of Concerns**: The project is divided into distinct layers (data, backend, AI, and frontend) to promote maintainability and scalability.

## Future Enhancements
- Integration of user feedback to improve emotion classification accuracy.
- Expansion of the song database to include more diverse genres and artists.
- Development of a mobile application to increase accessibility.

This design documentation will be updated as the project evolves and new features are implemented.