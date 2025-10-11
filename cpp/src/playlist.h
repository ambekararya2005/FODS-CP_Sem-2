#ifndef PLAYLIST_H
#define PLAYLIST_H

#include <string>
#include <vector>
#include <map>

struct Song {
    int id;
    std::string title;
    std::string artist;
    std::string lyrics;
    std::string emotion;
};

class EmotionPlaylist {
private:
    std::vector<Song> songs;
    std::map<std::string, std::vector<Song>> emotionIndex;
    
    void buildEmotionIndex();
    std::vector<std::string> parseCsvLine(const std::string& line);
    std::string trim(const std::string& str);
    std::string unquote(const std::string& str);
    
public:
    explicit EmotionPlaylist(const std::string& csvPath);
    
    // Load songs from CSV file
    void loadFromCsv(const std::string& csvPath);
    
    // Filter songs by one or more emotions
    std::vector<Song> filterByEmotions(const std::vector<std::string>& emotions) const;
    
    // Get all songs
    const std::vector<Song>& getAllSongs() const { return songs; }
    
    // Get all available emotions
    std::vector<std::string> getAvailableEmotions() const;
    
    // Convert songs to JSON string
    std::string toJson(const std::vector<Song>& songList) const;
};

#endif // PLAYLIST_H