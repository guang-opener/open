import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from models import WallpaperItem, ServerStatus
from scanner import scan_workshop, find_workshop_path, get_diagnostic_info, scan_export_folder

app = FastAPI(title="WallpaperSync Server", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_wallpaper_cache: list[WallpaperItem] = []
_custom_cache: list[WallpaperItem] = []
_workshop_path: str = ""
_steam_path: str = ""
_export_dir: str = r"D:\WallpaperExport"

def init_server(workshop_path: Optional[str] = None):
    global _workshop_path, _wallpaper_cache, _steam_path, _custom_cache
    if workshop_path and os.path.isdir(workshop_path):
        _workshop_path = workshop_path
        _steam_path = ""
    else:
        _workshop_path, _steam_path = find_workshop_path()
    if _workshop_path and os.path.isdir(_workshop_path):
        _wallpaper_cache = scan_workshop(_workshop_path)
        for item in _wallpaper_cache:
            if item.preview_path:
                item.preview_url = f"/api/wallpaper/{item.id}/preview"
            if item.wallpaper_type == "video":
                item.download_url = f"/api/wallpaper/{item.id}/download"
    # 扫描自定义导出文件夹
    _custom_cache = scan_export_folder(_export_dir)
    for item in _custom_cache:
        item.preview_url = f"/api/wallpaper/{item.id}/preview"
        if item.wallpaper_type == "video":
            item.download_url = f"/api/wallpaper/{item.id}/download"
    return _wallpaper_cache

@app.get("/api/status")
async def get_status():
    all_wps = _wallpaper_cache + _custom_cache
    return {
        "ok": True,
        "total_wallpapers": len(all_wps),
        "video_count": sum(1 for w in all_wps if w.wallpaper_type == "video"),
        "scene_count": sum(1 for w in all_wps if w.wallpaper_type == "scene"),
        "custom_count": len(_custom_cache),
        "export_dir": _export_dir,
        "workshop_path": _workshop_path,
        "version": "1.0.0",
    }

@app.get("/api/wallpapers")
async def get_wallpapers(page: int = Query(1, ge=1), size: int = Query(50, ge=1, le=200),
                         wallpaper_type: Optional[str] = Query(None, alias="type"),
                         search: Optional[str] = Query(None)):
    all_wps = _custom_cache + _wallpaper_cache
    filtered = list(all_wps)
    if wallpaper_type:
        filtered = [w for w in filtered if w.wallpaper_type == wallpaper_type]
    if search:
        keyword = search.lower()
        filtered = [w for w in filtered if keyword in w.name.lower() or keyword in w.author.lower()]
    total = len(filtered)
    start = (page - 1) * size
    end = start + size
    page_items = filtered[start:end]
    result_items = [{
        "id": item.id, "name": item.name, "author": item.author,
        "type": item.wallpaper_type, "sizeBytes": item.size_bytes,
        "previewUrl": item.preview_url, "downloadUrl": item.download_url,
        "contentRating": item.content_rating,
    } for item in page_items]
    return {"total": total, "page": page, "size": size, "hasMore": end < total, "items": result_items}

def _find_item(item_id: str):
    for item in _custom_cache + _wallpaper_cache:
        if item.id == item_id:
            return item
    return None

@app.get("/api/wallpaper/{item_id}")
async def get_wallpaper_detail(item_id: str):
    item = _find_item(item_id)
    if item:
        return {"id": item.id, "name": item.name, "author": item.author,
                "type": item.wallpaper_type, "sizeBytes": item.size_bytes,
                "previewUrl": item.preview_url, "downloadUrl": item.download_url}
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/api/wallpaper/{item_id}/preview")
async def get_wallpaper_preview(item_id: str):
    item = _find_item(item_id)
    if item and item.preview_path and os.path.isfile(item.preview_path):
        ext = os.path.splitext(item.preview_path)[1].lower()
        mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp", ".mp4": "video/mp4"}
        return FileResponse(item.preview_path, media_type=mime_map.get(ext, "application/octet-stream"))
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/api/wallpaper/{item_id}/download")
async def download_wallpaper(item_id: str):
    item = _find_item(item_id)
    if item and item.wallpaper_type == "video" and item.video_path and os.path.isfile(item.video_path):
        return FileResponse(item.video_path, media_type="video/mp4", filename=os.path.basename(item.video_path))
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/api/refresh")
async def refresh():
    global _wallpaper_cache, _custom_cache
    if _workshop_path:
        _wallpaper_cache = scan_workshop(_workshop_path)
        for item in _wallpaper_cache:
            if item.preview_path:
                item.preview_url = f"/api/wallpaper/{item.id}/preview"
            if item.wallpaper_type == "video":
                item.download_url = f"/api/wallpaper/{item.id}/download"
    _custom_cache = scan_export_folder(_export_dir)
    for item in _custom_cache:
        item.preview_url = f"/api/wallpaper/{item.id}/preview"
        if item.wallpaper_type == "video":
            item.download_url = f"/api/wallpaper/{item.id}/download"
    return {"ok": True, "count": len(_wallpaper_cache) + len(_custom_cache)}

@app.get("/api/diagnostic")
async def diagnostic():
    info = get_diagnostic_info()
    info["workshop_path_used"] = _workshop_path
    info["cache_count"] = len(_wallpaper_cache)
    return info

@app.get("/")
async def index():
    template = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    if os.path.isfile(template):
        return FileResponse(template, media_type="text/html")
    return JSONResponse({"message": "WallpaperSync Server running"})
