from dataclasses import dataclass, field
from typing import Optional

@dataclass
class WallpaperItem:
    id: str
    name: str
    author: str
    wallpaper_type: str
    preview_path: str
    video_path: str = ""
    folder_path: str = ""
    size_bytes: int = 0
    content_rating: str = "Everyone"
    preview_url: str = ""
    download_url: str = ""

@dataclass
class ServerStatus:
    ok: bool = True
    total_wallpapers: int = 0
    video_count: int = 0
    scene_count: int = 0
    workshop_path: str = ""
    version: str = "1.0.0"
