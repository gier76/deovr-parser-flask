from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import yt_dlp
import json
import os

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Global storage for parsed videos (simple in-memory cache)
parsed_videos = []

def parse_url(url: str):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
    }
    
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info and 'entries' in info:
                # It's a playlist or a page with multiple videos
                for entry in info['entries']:
                    if entry:
                        results.append({
                            "title": entry.get("title", "Unknown"),
                            "thumbnail": entry.get("thumbnail", ""),
                            "url": entry.get("url", ""),
                            "duration": entry.get("duration", 0)
                        })
            elif info:
                # It's a single video
                results.append({
                    "title": info.get("title", "Unknown"),
                    "thumbnail": info.get("thumbnail", ""),
                    "url": info.get("url", ""),
                    "duration": info.get("duration", 0)
                })
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
        
    return results

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "videos": parsed_videos})

@app.post("/parse", response_class=HTMLResponse)
async def handle_parse(request: Request, url: str = Form(...)):
    global parsed_videos
    parsed_videos = parse_url(url)
    return templates.TemplateResponse("index.html", {"request": request, "videos": parsed_videos, "success": True})

@app.get("/deovr")
async def get_deovr_json():
    # Construct the DeoVR Selection Scene JSON
    scenes_list = []
    
    for vid in parsed_videos:
        scenes_list.append({
            "title": vid["title"],
            "videoLength": vid["duration"],
            "thumbnailUrl": vid["thumbnail"],
            "video_url": vid["url"]
        })
    
    deovr_json = {
        "scenes": [
            {
                "name": "Web Results",
                "list": scenes_list
            }
        ]
    }
    
    return JSONResponse(content=deovr_json)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
