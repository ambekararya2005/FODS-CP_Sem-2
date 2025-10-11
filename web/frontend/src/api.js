export async function getEmotionPlaylist(userInput) {
    const response = await fetch('http://localhost:5000/api/classify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: userInput })
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    // The Flask API returns a JSON response from the C++ engine
    const data = await response.json();
    // Example: { emotion: "happy", playlist: [...] }
    return data;
}