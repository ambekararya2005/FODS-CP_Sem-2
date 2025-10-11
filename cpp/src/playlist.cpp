#include "playlist.h"
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <algorithm>
#include <set>
#include <iostream>

EmotionPlaylist::EmotionPlaylist(const std::string& csvPath) {
    loadFromCsv(csvPath);
}

std::string EmotionPlaylist::trim(const std::string& str) {
    size_t first = str.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) return "";
    size_t last = str.find_last_not_of(" \t\n\r");
    return str.substr(first, last - first + 1);
}

std::string EmotionPlaylist::unquote(const std::string& str) {
    std::string result = trim(str);
    if (result.length() >= 2 && result.front() == '"' && result.back() == '"') {
        return result.substr(1, result.length() - 2);
    }
    return result;
}

std::vector<std::string> EmotionPlaylist::parseCsvLine(const std::string& line) {
    std::vector<std::string> fields;
    std::string field;
    bool inQuotes = false;
    
    for (size_t i = 0; i < line.length(); ++i) {
        char c = line[i];
        
        if (c == '"') {
            inQuotes = !inQuotes;
            field += c;
        } else if (c == ',' && !inQuotes) {
            fields.push_back(unquote(field));
            field.clear();
        } else {
            field += c;
        }
    }
    
    fields.push_back(unquote(field));
    return fields;
}

void EmotionPlaylist::loadFromCsv(const std::string& csvPath) {
    std::ifstream file(csvPath);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open CSV file: " + csvPath);
    }
    
    songs.clear();
    
    std::string line;
    bool isHeader = true;
    
    while (std::getline(file, line)) {
        if (isHeader) {
            isHeader = false;
            continue;
        }
        
        if (line.empty()) continue;
        
        auto fields = parseCsvLine(line);
        
        if (fields.size() < 5) {
            std::cerr << "Warning: Skipping malformed line: " << line << std::endl;
            continue;
        }
        
        Song song;
        try {
            song.id = std::stoi(fields[0]);
            song.title = fields[1];
            song.artist = fields[2];
            song.lyrics = fields[3];
            song.emotion = fields[4];
            
            // Convert emotion to lowercase for case-insensitive matching
            std::transform(song.emotion.begin(), song.emotion.end(), 
                         song.emotion.begin(), ::tolower);
            
            songs.push_back(song);
        } catch (const std::exception& e) {
            std::cerr << "Warning: Error parsing line: " << line << std::endl;
        }
    }
    
    file.close();
    buildEmotionIndex();
}

void EmotionPlaylist::buildEmotionIndex() {
    emotionIndex.clear();
    for (const auto& song : songs) {
        emotionIndex[song.emotion].push_back(song);
    }
}

std::vector<Song> EmotionPlaylist::filterByEmotions(
    const std::vector<std::string>& emotions) const {
    
    std::set<int> uniqueIds;
    std::vector<Song> result;
    
    for (const auto& emotion : emotions) {
        std::string lowerEmotion = emotion;
        std::transform(lowerEmotion.begin(), lowerEmotion.end(), 
                      lowerEmotion.begin(), ::tolower);
        
        auto it = emotionIndex.find(lowerEmotion);
        if (it != emotionIndex.end()) {
            for (const auto& song : it->second) {
                if (uniqueIds.find(song.id) == uniqueIds.end()) {
                    uniqueIds.insert(song.id);
                    result.push_back(song);
                }
            }
        }
    }
    
    return result;
}

std::vector<std::string> EmotionPlaylist::getAvailableEmotions() const {
    std::vector<std::string> emotions;
    for (const auto& pair : emotionIndex) {
        emotions.push_back(pair.first);
    }
    return emotions;
}

std::string EmotionPlaylist::toJson(const std::vector<Song>& songList) const {
    std::ostringstream json;
    json << "{\"songs\": [";
    
    for (size_t i = 0; i < songList.size(); ++i) {
        const auto& song = songList[i];
        
        if (i > 0) json << ",";
        
        json << "\n  {\n"
             << "    \"id\": " << song.id << ",\n"
             << "    \"title\": \"" << song.title << "\",\n"
             << "    \"artist\": \"" << song.artist << "\",\n"
             << "    \"lyrics\": \"" << song.lyrics << "\",\n"
             << "    \"emotion\": \"" << song.emotion << "\"\n"
             << "  }";
    }
    
    json << "\n], \"count\": " << songList.size() << "}";
    return json.str();
}