"""
WallpaperSync PC Server - 双击启动
自动打开管理页面，无需任何配置
"""
import os, sys, socket, threading, time, webbrowser

import uvicorn
from server import app, init_server, _wallpaper_cache, _custom_cache
from scanner import get_diagnostic_info


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", "-p", type=str, default="")
    parser.add_argument("--port", type=int, default=18920)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    # 初始化
    items = init_server(args.path if args.path else None)
    video_count = sum(1 for w in items if w.wallpaper_type == "video")
    scene_count = sum(1 for w in items if w.wallpaper_type == "scene")
    custom_count = len(_custom_cache)

    ip = get_local_ip()
    local_url = f"http://localhost:{args.port}"
    phone_url = f"http://{ip}:{args.port}"

    print("=" * 50)
    print("  WallpaperSync PC Server v1.0.0")
    print("=" * 50)
    print(f"  壁纸总数: {len(items)}  |  视频: {video_count}")
    print(f"  场景: {scene_count}  |  自定义: {custom_count}")
    print(f"  管理页面: {local_url}")
    print(f"  手机连接: {phone_url}")
    print("=" * 50)

    # 启动 HTTP 服务
    server_thread = threading.Thread(
        target=uvicorn.run, args=(app,),
        kwargs={"host": args.host, "port": args.port, "log_level": "warning"},
        daemon=True
    )
    server_thread.start()
    time.sleep(1)

    # 打开管理页面
    webbrowser.open(local_url)

    print("  管理页面已打开，按 Ctrl+C 停止服务。")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("  已停止")


if __name__ == "__main__":
    main()
