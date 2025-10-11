#include <iostream>
#include <string>
#include <vector>
#include "playlist.h"

void printUsage(const char* programName) {
    std::cout << "Usage: " << programName << " <songs_csv_path> <emotions>\n";
    std::cout << "  emotions: comma-separated list (e.g., 'happy,excited')\n";
    std::cout << "\nExample:\n";
    std::cout << "  " << programName << " ../data/songs.csv happy,excited\n";
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        printUsage(argv[0]);
        return 1;
    }

    std::string csvPath = argv[1];
    std::string emotionsStr = argv[2];

    try {
        // Load songs from CSV
        EmotionPlaylist playlist(csvPath);
        
        // Parse emotions
        std::vector<std::string> emotions;
        size_t start = 0;
        size_t end = emotionsStr.find(',');
        
        while (end != std::string::npos) {
            emotions.push_back(emotionsStr.substr(start, end - start));
            start = end + 1;
            end = emotionsStr.find(',', start);
        }
        emotions.push_back(emotionsStr.substr(start));
        
        // Trim whitespace from emotions
        for (auto& emotion : emotions) {
            emotion.erase(0, emotion.find_first_not_of(" \t\n\r"));
            emotion.erase(emotion.find_last_not_of(" \t\n\r") + 1);
        }
        
        // Filter songs by emotions
        auto filteredSongs = playlist.filterByEmotions(emotions);
        
        // Output as JSON
        std::cout << playlist.toJson(filteredSongs) << std::endl;
        
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}