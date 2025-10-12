#include "playlist.h"
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <algorithm>
#include <iostream>
#include <regex>

EmotionPlaylist::EmotionPlaylist(const std::string& csvPath) : songHead(nullptr), emotionHead(nullptr) {
    loadFromCsv(csvPath);
}

EmotionPlaylist::~EmotionPlaylist() {
    clearSongList(songHead);
    clearEmotionList();
}

void EmotionPlaylist::clearSongList(SongNode* head) {
    SongNode* current = head;
    while (current != nullptr) {
        SongNode* next = current->next;
        delete current;
        current = next;
    }
}

void EmotionPlaylist::clearEmotionList() {
    EmotionNode* current = emotionHead;
    while (current != nullptr) {
        EmotionNode* next = current->next;
        clearSongList(current->songList);
        delete current;
        current = next;
    }
    emotionHead = nullptr;
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
            // Handle escaped quotes (two double quotes in a row)
            if (inQuotes && i + 1 < line.length() && line[i + 1] == '"') {
                field += '"';
                i++; // Skip the next quote
            } else {
                inQuotes = !inQuotes;
            }
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
    
    // Clear existing data
    clearSongList(songHead);
    songHead = nullptr;
    clearEmotionList();
    
    std::string line;
    bool isHeader = true;
    int lineNumber = 0;
    
    while (std::getline(file, line)) {
        lineNumber++;
        
        if (isHeader) {
            isHeader = false;
            continue;
        }
        
        if (line.empty()) continue;
        
        auto fields = parseCsvLine(line);
        
        if (fields.size() < 5) {
            std::cerr << "Warning: Skipping malformed line " << lineNumber 
                      << ": " << line << std::endl;
            continue;
        }
        
        Song song;
        try {
            song.id = std::stoi(fields[0]);
            song.title = fields[1];
            song.artist = fields[2];
            song.lyrics = fields[3];
            song.emotion = fields[4];
            
            // Validate fields
            if (song.title.empty() || song.artist.empty() || song.emotion.empty()) {
                std::cerr << "Warning: Skipping line " << lineNumber 
                          << " with empty required fields" << std::endl;
                continue;
            }
            
            // Convert emotion to lowercase for case-insensitive matching
            std::transform(song.emotion.begin(), song.emotion.end(), 
                         song.emotion.begin(), ::tolower);
            
            // Create a new node for the song
            SongNode* newNode = new SongNode(song);
            
            // Add to the main song list (singly linked list)
            if (songHead == nullptr) {
                songHead = newNode;
            } else {
                // Add to the end of the list
                SongNode* current = songHead;
                while (current->next != nullptr) {
                    current = current->next;
                }
                current->next = newNode;
            }
            
        } catch (const std::exception& e) {
            std::cerr << "Warning: Error parsing line " << lineNumber 
                      << ": " << e.what() << std::endl;
        }
    }
    
    file.close();
    
    if (songHead == nullptr) {
        std::cerr << "Warning: No valid songs found in " << csvPath << std::endl;
    }
    
    buildEmotionIndex();
}

EmotionNode* EmotionPlaylist::findEmotion(const std::string& emotion) const {
    EmotionNode* current = emotionHead;
    while (current != nullptr) {
        if (current->emotion == emotion) {
            return current;
        }
        current = current->next;
    }
    return nullptr;
}

void EmotionPlaylist::addSongToEmotion(EmotionNode* emotionNode, const Song& song) {
    SongNode* newNode = new SongNode(song);
    
    if (emotionNode->songList == nullptr) {
        emotionNode->songList = newNode;
    } else {
        // Add to the end of the list
        SongNode* current = emotionNode->songList;
        while (current->next != nullptr) {
            current = current->next;
        }
        current->next = newNode;
    }
}

void EmotionPlaylist::buildEmotionIndex() {
    // Clear existing emotion index
    clearEmotionList();
    
    // Iterate through all songs and build the emotion index
    SongNode* current = songHead;
    while (current != nullptr) {
        const Song& song = current->data;
        
        // Find or create emotion node
        EmotionNode* emotionNode = findEmotion(song.emotion);
        
        if (emotionNode == nullptr) {
            // Create a new emotion node
            emotionNode = new EmotionNode(song.emotion);
            
            // Add to the doubly linked list of emotions
            if (emotionHead == nullptr) {
                emotionHead = emotionNode;
            } else {
                // Add to the end of the list
                EmotionNode* lastEmotion = emotionHead;
                while (lastEmotion->next != nullptr) {
                    lastEmotion = lastEmotion->next;
                }
                lastEmotion->next = emotionNode;
                emotionNode->prev = lastEmotion;
            }
        }
        
        // Add song to the emotion's song list
        addSongToEmotion(emotionNode, song);
        
        current = current->next;
    }
}

bool EmotionPlaylist::songExistsInList(SongNode* head, int songId) const {
    SongNode* current = head;
    while (current != nullptr) {
        if (current->data.id == songId) {
            return true;
        }
        current = current->next;
    }
    return false;
}

SongNode* EmotionPlaylist::filterByEmotions(const std::vector<std::string>& emotions) const {
    if (emotions.empty()) {
        // Return a copy of all songs if no emotions specified
        SongNode* resultHead = nullptr;
        SongNode* resultTail = nullptr;
        
        SongNode* current = songHead;
        while (current != nullptr) {
            SongNode* newNode = new SongNode(current->data);
            
            if (resultHead == nullptr) {
                resultHead = newNode;
                resultTail = newNode;
            } else {
                resultTail->next = newNode;
                resultTail = newNode;
            }
            
            current = current->next;
        }
        
        return resultHead;
    }
    
    SongNode* resultHead = nullptr;
    SongNode* resultTail = nullptr;
    
    for (const auto& emotion : emotions) {
        if (emotion.empty()) continue;
        
        std::string lowerEmotion = emotion;
        std::transform(lowerEmotion.begin(), lowerEmotion.end(), 
                      lowerEmotion.begin(), ::tolower);
        
        EmotionNode* emotionNode = findEmotion(lowerEmotion);
        
        if (emotionNode != nullptr) {
            SongNode* current = emotionNode->songList;
            
            while (current != nullptr) {
                // Check if song already exists in result list to avoid duplicates
                if (!songExistsInList(resultHead, current->data.id)) {
                    SongNode* newNode = new SongNode(current->data);
                    
                    if (resultHead == nullptr) {
                        resultHead = newNode;
                        resultTail = newNode;
                    } else {
                        resultTail->next = newNode;
                        resultTail = newNode;
                    }
                }
                
                current = current->next;
            }
        }
    }
    
    return resultHead;
}

std::vector<std::string> EmotionPlaylist::getAvailableEmotions() const {
    std::vector<std::string> emotions;
    
    EmotionNode* current = emotionHead;
    while (current != nullptr) {
        emotions.push_back(current->emotion);
        current = current->next;
    }
    
    return emotions;
}

std::string EmotionPlaylist::escapeJsonString(const std::string& input) const {
    std::string output;
    output.reserve(input.length() * 1.1); // Reserve a bit more space
    
    for (char c : input) {
        switch (c) {
            case '\"': output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\b': output += "\\b"; break;
            case '\f': output += "\\f"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default:
                if (static_cast<unsigned char>(c) < 32) {
                    // For control characters, use \u00XX format
                    char buf[7];
                    snprintf(buf, sizeof(buf), "\\u%04x", c);
                    output += buf;
                } else {
                    output += c;
                }
        }
    }
    
    return output;
}

std::string EmotionPlaylist::toJson(SongNode* songList) const {
    std::ostringstream json;
    json << "{\"songs\": [";
    
    SongNode* current = songList;
    bool isFirst = true;
    int count = 0;
    
    while (current != nullptr) {
        if (!isFirst) {
            json << ",";
        }
        isFirst = false;
        
        const auto& song = current->data;
        
        json << "\n  {\n"
             << "    \"id\": " << song.id << ",\n"
             << "    \"title\": \"" << escapeJsonString(song.title) << "\",\n"
             << "    \"artist\": \"" << escapeJsonString(song.artist) << "\",\n"
             << "    \"lyrics\": \"" << escapeJsonString(song.lyrics) << "\",\n"
             << "    \"emotion\": \"" << escapeJsonString(song.emotion) << "\"\n"
             << "  }";
        
        count++;
        current = current->next;
    }
    
    json << "\n], \"count\": " << count << "}";
    return json.str();
}
