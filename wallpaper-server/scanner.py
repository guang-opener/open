import json, os, re, sys
from typing import List, Tuple
from models import WallpaperItem

WE_APP_ID = "431960"
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".avi", ".mov", ".wmv"}

def find_workshop_path() -> Tuple[str, str]:
    steam_path = _get_steam_path_from_registry()
    if steam_path:
        workshop = _check_workshop_at_steam(steam_path)
        if workshop:
            return workshop, steam_path
    workshop = _search_all_drives()
    if workshop:
        return workshop, ""
    workshop = _search_libraryfolders_all_drives()
    if workshop:
        return workshop, ""
    return "", ""

def _get_steam_path_from_registry() -> str:
    if sys.platform != 'win32':
        return ""
    try:
        import winreg
        for hive, key_path in [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam"),
        ]:
            try:
                key = winreg.OpenKey(hive, key_path)
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                winreg.CloseKey(key)
                if install_path and os.path.isdir(install_path):
                    return install_path
            except (OSError, FileNotFoundError):
                continue
    except ImportError:
        pass
    return ""

def _check_workshop_at_steam(steam_install_path: str) -> str:
    main_workshop = os.path.join(steam_install_path, "steamapps", "workshop", "content", WE_APP_ID)
    if os.path.isdir(main_workshop):
        return main_workshop
    vdf_path = os.path.join(steam_install_path, "steamapps", "libraryfolders.vdf")
    if not os.path.isfile(vdf_path):
        vdf_path = os.path.join(steam_install_path, "config", "libraryfolders.vdf")
    if os.path.isfile(vdf_path):
        extra_paths = _parse_libraryfolders_vdf(vdf_path)
        for lib_path in extra_paths:
            workshop = os.path.join(lib_path, "steamapps", "workshop", "content", WE_APP_ID)
            if os.path.isdir(workshop):
                return workshop
    return ""

def _parse_libraryfolders_vdf(config_path: str) -> List[str]:
    paths = []
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return paths
    matches = re.findall(r'"path"\s+"([^"]+)"', content)
    for p in matches:
        p = p.replace("\\\\", "\\")
        if os.path.isdir(p):
            paths.append(p)
    return paths

def _search_all_drives() -> str:
    import string
    library_names = ["SteamLibrary", "Steam", "SteamGames", "Games"]
    for drive_letter in string.ascii_uppercase[2:]:
        drive_root = f"{drive_letter}:\\"
        if not os.path.exists(drive_root):
            continue
        for lib_name in library_names:
            workshop = os.path.join(drive_root, lib_name, "steamapps", "workshop", "content", WE_APP_ID)
            if os.path.isdir(workshop):
                return workshop
    for prog in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"]:
        workshop = os.path.join(prog, "steamapps", "workshop", "content", WE_APP_ID)
        if os.path.isdir(workshop):
            return workshop
    return ""

def _search_libraryfolders_all_drives() -> str:
    import string
    vdf_relative_paths = [
        "SteamLibrary/steamapps/libraryfolders.vdf",
        "Steam/steamapps/libraryfolders.vdf",
        "Steam/config/libraryfolders.vdf",
        "Program Files (x86)/Steam/steamapps/libraryfolders.vdf",
        "Program Files/Steam/steamapps/libraryfolders.vdf",
    ]
    for drive_letter in string.ascii_uppercase[2:]:
        drive_root = f"{drive_letter}:\\"
        if not os.path.exists(drive_root):
            continue
        for rel_path in vdf_relative_paths:
            vdf_path = os.path.join(drive_root, rel_path)
            if os.path.isfile(vdf_path):
                lib_paths = _parse_libraryfolders_vdf(vdf_path)
                for lib_path in lib_paths:
                    workshop = os.path.join(lib_path, "steamapps", "workshop", "content", WE_APP_ID)
                    if os.path.isdir(workshop):
                        return workshop
    return ""

def get_diagnostic_info() -> dict:
    info = {
        "steam_installed": False, "steam_path": "", "library_folders": [],
        "we_workshop_found": False, "we_workshop_path": "",
        "has_wallpapers": False, "wallpaper_count": 0,
    }
    steam_path = _get_steam_path_from_registry()
    if steam_path:
        info["steam_installed"] = True
        info["steam_path"] = steam_path
        vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
        if not os.path.isfile(vdf_path):
            vdf_path = os.path.join(steam_path, "config", "libraryfolders.vdf")
        if os.path.isfile(vdf_path):
            info["library_folders"] = _parse_libraryfolders_vdf(vdf_path)
        info["library_folders"].insert(0, steam_path)
        for lib in info["library_folders"]:
            workshop = os.path.join(lib, "steamapps", "workshop", "content", WE_APP_ID)
            if os.path.isdir(workshop):
                info["we_workshop_found"] = True
                info["we_workshop_path"] = workshop
                items = os.listdir(workshop)
                info["wallpaper_count"] = len([d for d in items if os.path.isdir(os.path.join(workshop, d))])
                info["has_wallpapers"] = info["wallpaper_count"] > 0
                break
    return info

def scan_workshop(workshop_path: str) -> List[WallpaperItem]:
    items = []
    if not workshop_path or not os.path.isdir(workshop_path):
        return items
    for folder_name in sorted(os.listdir(workshop_path)):
        folder_path = os.path.join(workshop_path, folder_name)
        if not os.path.isdir(folder_path):
            continue
        item = _parse_wallpaper_folder(folder_name, folder_path)
        if item:
            items.append(item)
    return items

def _parse_wallpaper_folder(item_id: str, folder_path: str) -> WallpaperItem:
    project_json = None
    for name in ["project.json", "scene.json"]:
        p = os.path.join(folder_path, name)
        if os.path.isfile(p):
            project_json = p
            break
    name = item_id
    author = "Unknown"
    rating = "Everyone"
    try:
        if project_json:
            with open(project_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("title") or data.get("projectname") or item_id
            author = data.get("author") or "Unknown"
            rating = data.get("contentrating", "Everyone")
    except (json.JSONDecodeError, IOError):
        pass

    preview_path = ""
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        for prefix in ["preview", "thumbnail"]:
            pc = os.path.join(folder_path, f"{prefix}{ext}")
            if os.path.isfile(pc):
                preview_path = pc
                break
        if preview_path:
            break
    if not preview_path:
        for f in sorted(os.listdir(folder_path)):
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                preview_path = os.path.join(folder_path, f)
                break

    video_path = ""
    wallpaper_type = "scene"
    size_bytes = 0
    for f in sorted(os.listdir(folder_path)):
        ext = os.path.splitext(f)[1].lower()
        if ext in VIDEO_EXTENSIONS:
            video_path = os.path.join(folder_path, f)
            wallpaper_type = "video"
            size_bytes = os.path.getsize(video_path)
            break

    if not project_json and not video_path:
        has_html = any(f.endswith(".html") or f.endswith(".htm") for f in os.listdir(folder_path))
        wallpaper_type = "web" if has_html else "unknown"

    return WallpaperItem(
        id=item_id, name=name, author=author,
        wallpaper_type=wallpaper_type, preview_path=preview_path,
        video_path=video_path, folder_path=folder_path, size_bytes=size_bytes,
        content_rating=rating,
    )


# ============================================================
# 自定义导出文件夹扫描（.mpkg 解压提取）
# ============================================================

DEFAULT_EXPORT_DIR = r"D:\WallpaperExport"


def scan_export_folder(export_dir: str = "") -> List[WallpaperItem]:
    """扫描自定义导出文件夹，收集 MP4 视频"""
    if not export_dir or not os.path.isdir(export_dir):
        export_dir = DEFAULT_EXPORT_DIR

    if not os.path.isdir(export_dir):
        os.makedirs(export_dir, exist_ok=True)
        return []

    items: List[WallpaperItem] = []

    for fname in sorted(os.listdir(export_dir)):
        fpath = os.path.join(export_dir, fname)
        if fname.lower().endswith('.mp4'):
            item = _wrap_video_item(fpath, fname, export_dir)
            if item:
                items.append(item)

    return items


def _wrap_video_item(mp4_path: str, fname: str, export_dir: str) -> WallpaperItem | None:
    """将裸 MP4 文件包装为 WallpaperItem"""
    base_name = os.path.splitext(fname)[0]
    item_id = "video_" + base_name
    return WallpaperItem(
        id=item_id,
        name=base_name,
        author="自定义视频",
        wallpaper_type="video",
        preview_path=mp4_path,
        video_path=mp4_path,
        folder_path=export_dir,
        size_bytes=os.path.getsize(mp4_path),
    )
