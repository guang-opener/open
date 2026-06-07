/**
 * WallpaperSync — 壁纸数据模型
 */

export class RemoteWallpaperItem {
  id: string = ''
  name: string = ''
  author: string = ''
  type: string = ''     // "video" | "scene" | "web"
  sizeBytes: number = 0
  previewUrl: string = ''
  downloadUrl: string = ''
  contentRating: string = 'Everyone' // "Everyone" | "Mature" | "Unknown"
}

export class LocalWallpaperItem {
  id: string = ''
  name: string = ''
  author: string = ''
  localPath: string = ''
  sizeBytes: number = 0
  downloadTime: number = 0
}

export class ServerStatus {
  ok: boolean = false
  totalWallpapers: number = 0
  videoCount: number = 0
  sceneCount: number = 0
  workshopPath: string = ''
  version: string = ''
}

export class WallpaperListResponse {
  total: number = 0
  page: number = 1
  size: number = 50
  hasMore: boolean = false
  items: RemoteWallpaperItem[] = []
}
