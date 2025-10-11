import React, { useState } from 'react';
import { Music, Send, Loader2, Heart, Smile, Frown, Zap, Coffee, Moon } from 'lucide-react';

const App = () => {
  const [userInput, setUserInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const emotionIcons = {
    joy: Smile,
    sadness: Frown,
    love: Heart,
    anger: Zap,
    fear: Moon,
    surprise: Coffee
  };

  const emotionColors = {
    joy: 'from-yellow-400 to-orange-500',
    sadness: 'from-blue-400 to-blue-600',
    love: 'from-pink-400 to-red-500',
    anger: 'from-red-500 to-red-700',
    fear: 'from-purple-400 to-purple-600',
    surprise: 'from-green-400 to-teal-500'
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:5000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: userInput }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze emotion. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const EmotionIcon = result?.emotion ? emotionIcons[result.emotion.toLowerCase()] || Music : Music;
  const gradientColor = result?.emotion ? emotionColors[result.emotion.toLowerCase()] || 'from-gray-400 to-gray-600' : 'from-purple-500 to-pink-500';

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob top-0 -left-4"></div>
        <div className="absolute w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000 top-0 -right-4"></div>
        <div className="absolute w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000 bottom-0 left-1/2"></div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Music className="w-12 h-12 text-pink-400" />
            <h1 className="text-5xl font-bold text-white">Emotion Playlist</h1>
          </div>
          <p className="text-gray-300 text-lg">
            Share how you're feeling, and we'll create the perfect playlist for you
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-2xl border border-white/20">
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="How are you feeling today? Describe your mood..."
              className="w-full bg-white/5 text-white placeholder-gray-400 rounded-xl p-4 border border-white/20 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none"
              rows="4"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !userInput.trim()}
              className="mt-4 w-full bg-gradient-to-r from-pink-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-xl hover:from-pink-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2 shadow-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Generate Playlist
                </>
              )}
            </button>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/20 backdrop-blur-lg border border-red-500/50 rounded-xl p-4 mb-8 text-red-200">
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Emotion Card */}
            <div className={`bg-gradient-to-r ${gradientColor} rounded-2xl p-6 shadow-2xl text-white`}>
              <div className="flex items-center gap-4 mb-4">
                <div className="bg-white/20 p-3 rounded-xl">
                  <EmotionIcon className="w-8 h-8" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold">Detected Emotion</h2>
                  <p className="text-white/90 capitalize text-xl">{result.emotion}</p>
                </div>
              </div>
              <div className="bg-white/20 rounded-xl p-3">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-semibold">Confidence</span>
                  <span className="text-sm font-bold">{(result.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-white/30 rounded-full h-2">
                  <div
                    className="bg-white h-2 rounded-full transition-all duration-500"
                    style={{ width: `${result.confidence * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Playlist */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 shadow-2xl border border-white/20">
              <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                <Music className="w-6 h-6 text-pink-400" />
                Your Personalized Playlist
              </h3>
              <div className="space-y-3">
                {result.playlist && result.playlist.length > 0 ? (
                  result.playlist.map((song, index) => (
                    <div
                      key={index}
                      className="bg-white/5 hover:bg-white/10 transition-all duration-200 rounded-xl p-4 border border-white/10 hover:border-pink-500/50"
                    >
                      <div className="flex items-start gap-4">
                        <div className="bg-gradient-to-br from-pink-500 to-purple-600 text-white font-bold w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <h4 className="text-white font-semibold text-lg">{song.title}</h4>
                          <p className="text-gray-300">{song.artist}</p>
                          {song.genre && (
                            <span className="inline-block mt-2 px-3 py-1 bg-purple-500/30 text-purple-200 rounded-full text-xs font-semibold">
                              {song.genre}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-400 text-center py-8">No songs available for this emotion</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!result && !loading && !error && (
          <div className="bg-white/5 backdrop-blur-lg rounded-2xl p-12 text-center border border-white/10">
            <Music className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-300 mb-2">Ready to discover your soundtrack?</h3>
            <p className="text-gray-400">Tell us how you're feeling and let AI curate the perfect playlist</p>
          </div>
        )}
      </div>

      <style>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
};

export default App;