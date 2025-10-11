# Emotion Playlist

## Overview
The Emotion Playlist project is designed to create personalized music playlists based on the emotional content of song lyrics. By analyzing the lyrics, the application classifies emotions and generates playlists that match the user's mood.

## Project Structure
The project is organized into several directories, each serving a specific purpose:

- **data/**: Contains seed data for songs and example lyrics.
- **cpp/**: Implements the core functionality of the application in C++.
- **ai/**: Contains scripts for emotion classification and model training.
- **web/**: Hosts the frontend and backend components of the web application.
- **onnx/**: (Optional) Contains files for exporting models in ONNX format.
- **docs/**: Contains design documentation for the project.

## Setup Instructions

### Prerequisites
- C++ compiler (e.g., g++)
- Python 3.x
- Node.js and npm

### C++ Setup
1. Navigate to the `cpp` directory.
2. Build the project using CMake:
   ```
   mkdir build
   cd build
   cmake ..
   make
   ```

### AI Setup
1. Navigate to the `ai` directory.
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

### Web Setup
1. Navigate to the `web/frontend` directory.
2. Install the required Node.js packages:
   ```
   npm install
   ```
3. Start the frontend application:
   ```
   npm start
   ```

4. Navigate to the `web/backend` directory.
5. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
6. Start the Flask API:
   ```
   python app.py
   ```

## Usage Guidelines
- Use the CLI application in the `cpp` directory to interact with the playlist functionality.
- The AI scripts in the `ai` directory can be used to classify emotions based on lyrics and fine-tune the model.
- The web application allows users to interact with the system through a user-friendly interface.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.