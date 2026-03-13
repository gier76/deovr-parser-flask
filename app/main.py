from flask import Flask, request, render_template_string, jsonify
import yt_dlp
import requests
import re
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
        .container { max-width: 800px; width: 100%; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        input { width: 70%; padding: 12px; border-radius: 5px; border: 1px solid #444; background: #2a2a2a; color: white; }
        button { padding: 12px 24px; background: #00bcd4; border: none; color: white; cursor: pointer; border-radius: 5px; font-weight: bold; }
        button:hover { background: #0097a7; }
        .video { display: flex; gap: 15px; margin-top: 15px; background: #2a2a2a; padding: 15px; border-radius: 8px; align-items: center; transition: transform 0.2s; }
        .video:hover { transform: scale(1.01); background: #333; }
        img { width: 150px; border-radius: 5px; }
        .info { flex-grow: 1; }
        .deovr-link { display: inline-block; margin-top: 20px; padding: 12px 24px; background: #333; color: #00bcd4; text-decoration: none; border-radius: 5px; font-weight: bold; border: 1px solid #00bcd4; }
        .loader { color: #888; font-style: italic; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DeoVR Web Parser (Flask)</h1>
        <p style="font-size: 0.9em; color: #888;">Unterstützt eporner (Videos & Tags), youtube und mehr.</p>
        
        <form method="POST" action="">
            <input type="text" name="url" placeholder="URL eingeben (z.B. eporner tag seite)..." required>
            <button type="submit">Parsen</button>
        </form>

        {% if videos %}
            <h3 style="margin-top: 30px;">Gefundene Videos: {{ videos|length }}</h3>
            <div class="results">
                {% for video in videos %}
                    <div class="video">
                        <img src="{{ video.thumbnail }}" alt="Thumbnail">
                        <div class="info">
                            <div style="font-weight: bold; color: #00bcd4;">{{ video.title }}</div>
                            <div style="color: #888; font-size: 0.8em; margin-top: 5px;">Dauer: {{ video.duration }}s</div>
                        </div>
                    </div>
                {% endfor %}
            </div>
            
            <div style="text-align: center;">
                <a href="deovr" class="deovr-link">🔗 DeoVR JSON für Player öffnen</a>
                <p style="font-size: 0.8em; color: #666; margin-top: 10px;">
                    Gib im DeoVR Browser ein: <br>
                    <code>http://[DEINE-HA-IP]:8080/deovr</code>
                </p>
            </div>
        {% elif has_posted %}
            <p style="color: #ff5252; margin-top: 20px; text-align: center;">Keine Videos gefunden oder Fehler beim Parsen.</p>
        {% endif %}
    </div>
</body>
</html>
"""

def extract_eporner_tag_page(url):
    results = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text
        
        # Regex to find video links on eporner
        # Format: <a href="/hd-porn/MBvIsFrv6Sc/..." title="Title">
        # and thumbnails: <img src="https://static-eu-cdn.eporner.com/thumbs/static/.../img.jpg"
        
        # Find all video containers
        video_blocks = re.findall(r'<div class="post-g">.*?<a href="(/hd-porn/.*?/)".*?title="(.*?)".*?src="(.*?)"', html, re.DOTALL)
        
        for link, title, thumb in video_blocks:
            full_url = "https://www.eporner.com" + link
            results.append({
                "title": title,
                "thumbnail": thumb,
                "url": full_url,
                "duration": 0 # Duration extraction needs more regex or secondary requests
            })
            if len(results) >= 20: break # Limit to 20 for speed
            
    except Exception as e:
        print(f"Eporner extraction error: {e}")
    return results

def parse_url(url):
    if not url: return []
    
    # Check if it's an eporner tag/search page
    if "eporner.com" in url and ("/tag/" in url or "/search/" in url):
        return extract_eporner_tag_page(url)
        
    # Default yt-dlp extraction
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
            if not info: return []
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
        print(f"yt-dlp error: {e}")
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
    return jsonify({"scenes": [{"name": "Parser Results", "list": scenes}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
