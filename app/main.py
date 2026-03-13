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
        input { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #00bcd4; border: none; color: white; cursor: pointer; }
        .video { display: flex; gap: 10px; margin-top: 10px; background: #2a2a2a; padding: 10px; }
        img { width: 100px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DeoVR Web Parser (Flask)</h1>
        <form method="POST" action="/parse">
            <input type="text" name="url" placeholder="Video URL" required>
            <button type="submit">Parsen</button>
        </form>
        {% if videos %}
            <h3>Gefunden: {{ videos|length }}</h3>
            {% for video in videos %}
                <div class="video">
                    <img src="{{ video.thumbnail }}">
                    <div>{{ video.title }}<br><small>{{ video.duration }}s</small></div>
                </div>
            {% endfor %}
            <a href="/deovr" style="color: #00bcd4; display: block; margin-top: 20px;">JSON für DeoVR</a>
        {% endif %}
    </div>
</body>
</html>
"""

def parse_url(url):
    ydl_opts = {'quiet': True, 'extract_flat': 'in_playlist'}
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            entries = info.get('entries', [info])
            for entry in entries:
                if entry:
                    results.append({
                        "title": entry.get("title", "Unknown"),
                        "thumbnail": entry.get("thumbnail", ""),
                        "url": entry.get("url", ""),
                        "duration": entry.get("duration", 0)
                    })
    except Exception as e:
        print(f"Error: {e}")
    return results

@app.route("/")
def home():
    return render_template_string(INDEX_HTML, videos=parsed_videos)

@app.route("/parse", methods=["POST"])
def handle_parse():
    global parsed_videos
    url = request.form.get("url")
    parsed_videos = parse_url(url)
    return render_template_string(INDEX_HTML, videos=parsed_videos)

@app.route("/deovr")
def get_deovr():
    scenes = [{"title": v["title"], "videoLength": v["duration"], "thumbnailUrl": v["thumbnail"], "video_url": v["url"]} for v in parsed_videos]
    return jsonify({"scenes": [{"name": "Flask Results", "list": scenes}]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
