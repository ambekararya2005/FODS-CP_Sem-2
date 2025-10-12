#ifndef PLAYLIST_H
#define PLAYLIST_H

#include <string>
#include <vector>

// Song structure remains the same
struct Song {
    int id;
    std::string title;
    std::string artist;
    std::string lyrics;
    std::string emotion;
};

// Singly linked list node for songs
struct SongNode {
    Song data;
    SongNode* next;
    
    SongNode(const Song& song) : data(song), next(nullptr) {}
};

// Doubly linked list node for emotions
struct EmotionNode {
    std::string emotion;
    SongNode* songList; // Points to a singly linked list of songs
    EmotionNode* prev;
    EmotionNode* next;
    
    EmotionNode(const std::string& e) : emotion(e), songList(nullptr), prev(nullptr), next(nullptr) {}
};

class EmotionPlaylist {
private:
    SongNode* songHead; // Head of the singly linked list of all songs
    EmotionNode* emotionHead; // Head of the doubly linked list of emotions
    
    void buildEmotionIndex();
    std::vector<std::string> parseCsvLine(const std::string& line);
    std::string trim(const std::string& str);
    std::string unquote(const std::string& str);
    std::string escapeJsonString(const std::string& input) const;
    
    // Helper methods for linked list operations
    void clearSongList(SongNode* head);
    void clearEmotionList();
    EmotionNode* findEmotion(const std::string& emotion) const;
    void addSongToEmotion(EmotionNode* emotionNode, const Song& song);
    bool songExistsInList(SongNode* head, int songId) const;
    
public:
    EmotionPlaylist(const std::string& csvPath);
    ~EmotionPlaylist(); // Destructor to free memory
    
    // Load songs from CSV file
    void loadFromCsv(const std::string& csvPath);
    
    // Filter songs by one or more emotions
    SongNode* filterByEmotions(const std::vector<std::string>& emotions) const;
    
    // Get all songs
    SongNode* getAllSongs() const { return songHead; }
    
    // Get all available emotions
    std::vector<std::string> getAvailableEmotions() const;
    
    // Convert songs to JSON string
    std::string toJson(SongNode* songList) const;
};

#endif // PLAYLIST_H
