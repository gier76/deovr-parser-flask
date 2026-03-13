from flask import Flask, request, render_template_string, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Global storage for parsed videos
parsed_videos = []

INDEX_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>DeoVR Web Parser Flask</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { max-width: 800px; width: 100%; background: #1e1e1e; padding: 20px; border-radius: 10px; }
        input { width: 70%; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #2a2a2a; color: white; }
        button { padding: 10px 20px; background: #00bcd4; border: none; color: white; cursor: pointer; border-radius: 5px; font-weight: bold; }
        button:hover { background: #0097a7; }
        .video { display: flex; gap: 15px; margin-top: 15px; background: #2a2a2a; padding: 15px; border-radius: 8px; align-items: center; }
        img { width: 150px; border-radius: 5px; }
        .deovr-link { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #333; color: #00bcd4; text-decoration: none; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DeoVR Web Parser (Flask)</h1>
        <p style="font-size: 0.9em; color: #888;">Kompatibel mit eporner, youtube und hunderten weiteren Seiten.</p>
        
        <form method="POST" action="">
            <input type="text" name="url" placeholder="Video- oder Tag-URL eingeben..." required>
            <button type="submit">Parsen</button>
        </form>

        {% if videos %}
            <h3 style="margin-top: 30px;">Gefundene Videos: {{ videos|length }}</h3>
            <div class="results">
                {% for video in videos %}
                    <div class="video">
                        <img src="{{ video.thumbnail }}" alt="Thumbnail">
                        <div class="info">
                            <div style="font-weight: bold;">{{ video.title }}</div>
                            <div style="color: #888; font-size: 0.8em;">Dauer: {{ video.duration }}s</div>
                        </div>
                    </div>
                {% endfor %}
            </div>
            
            <a href="deovr" class="deovr-link">🔗 DeoVR JSON für Player öffnen</a>
            <p style="font-size: 0.8em; color: #666; margin-top: 10px;">
                Adresse für DeoVR Browser: <br>
                <code>http://[DEINE-HA-IP]:8080/deovr</code>
            </p>
        {% elif has_posted %}
            <p style="color: #ff5252; margin-top: 20px;">Keine Videos gefunden oder Fehler beim Parsen.</p>
        {% endif %}
    </div>
</body>
</html>
"""

def parse_url(url):
    if not url:
        return []
    # yt-dlp options for metadata extraction
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'dump_single_json': True,
    }
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return []
                
            entries = info.get('entries', [info])
            for entry in entries:
                if entry:
                    results.append({
                        "title": entry.get("title", "Unknown"),
                        "thumbnail": entry.get("thumbnail", ""),
                        "url": entry.get("url", entry.get("webpage_url", "")),
                        "duration": entry.get("duration", 0)
                    })
    except Exception as e:
        print(f"Parsing error: {e}")
    return results

@app.route("/", methods=["GET", "POST"])
def home():
    global parsed_videos
    has_posted = False
    if request.method == "POST":
        has_posted = True
        url = request.form.get("url")
        parsed_videos = parse_url(url)
    return render_template_string(INDEX_HTML, videos=parsed_videos, has_posted=has_posted)

@app.route("/deovr")
def get_deovr():
    scenes = []
    for v in parsed_videos:
        scenes.append({
            "title": v["title"],
            "videoLength": v["duration"],
            "thumbnailUrl": v["thumbnail"],
            "video_url": v["url"]
        })
    
    return jsonify({
        "scenes": [
            {
                "name": "Web Results",
                "list": scenes
            }
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
