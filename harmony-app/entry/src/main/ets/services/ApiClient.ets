/**
 * WallpaperSync — API 客户端
 */
import { http } from '@kit.NetworkKit';
import { RemoteWallpaperItem, ServerStatus, WallpaperListResponse } from '../models/WallpaperItem';

export class ApiClient {
  private baseUrl: string = '';

  constructor(baseUrl: string) {
    if (!baseUrl.startsWith('http://') && !baseUrl.startsWith('https://')) {
      baseUrl = 'http://' + baseUrl;
    }
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  setBaseUrl(url: string): void {
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://' + url;
    }
    this.baseUrl = url.replace(/\/+$/, '');
  }

  async getStatus(): Promise<ServerStatus> {
    const resp = await this._get('/api/status');
    const data = JSON.parse(resp) as Record<string, Object>;
    const status = new ServerStatus();
    status.ok = (data['ok'] as boolean) ?? false;
    status.totalWallpapers = (data['total_wallpapers'] as number) ?? 0;
    status.videoCount = (data['video_count'] as number) ?? 0;
    status.sceneCount = (data['scene_count'] as number) ?? 0;
    status.workshopPath = (data['workshop_path'] as string) ?? '';
    status.version = (data['version'] as string) ?? '';
    return status;
  }

  async getWallpapers(
    page: number = 1,
    size: number = 50,
    typeFilter: string = '',
    search: string = ''
  ): Promise<WallpaperListResponse> {
    let url = `/api/wallpapers?page=${page}&size=${size}`;
    if (typeFilter) {
      url += `&type=${encodeURIComponent(typeFilter)}`;
    }
    if (search) {
      url += `&search=${encodeURIComponent(search)}`;
    }
    const resp = await this._get(url);
    const data = JSON.parse(resp) as Record<string, Object>;

    const result = new WallpaperListResponse();
    result.total = (data['total'] as number) ?? 0;
    result.page = (data['page'] as number) ?? page;
    result.size = (data['size'] as number) ?? size;
    result.hasMore = (data['hasMore'] as boolean) ?? false;

    const items = (data['items'] as Array<Record<string, Object>>) ?? [];
    result.items = items.map((item: Record<string, Object>) => {
      const w = new RemoteWallpaperItem();
      w.id = (item['id'] as string) ?? '';
      w.name = (item['name'] as string) ?? '';
      w.author = (item['author'] as string) ?? '';
      w.type = (item['type'] as string) ?? '';
      w.sizeBytes = (item['sizeBytes'] as number) ?? 0;
      w.contentRating = (item['contentRating'] as string) ?? 'Everyone';
      w.previewUrl = this.baseUrl + ((item['previewUrl'] as string) ?? '');
      w.downloadUrl = this.baseUrl + ((item['downloadUrl'] as string) ?? '');
      return w;
    });

    return result;
  }

  getPreviewUrl(itemId: string): string {
    return `${this.baseUrl}/api/wallpaper/${itemId}/preview`;
  }

  getDownloadUrl(itemId: string): string {
    return `${this.baseUrl}/api/wallpaper/${itemId}/download`;
  }

  async refreshServer(): Promise<boolean> {
    try {
      await this._get('/api/refresh');
      return true;
    } catch (_e) {
      return false;
    }
  }

  private async _get(path: string): Promise<string> {
    const fullUrl = this.baseUrl + path;
    const request = http.createHttp();
    try {
      const response = await request.request(
        fullUrl,
        {
          method: http.RequestMethod.GET,
          connectTimeout: 5000,
          readTimeout: 15000,
        }
      );
      if (response.responseCode === 200) {
        return response.result as string;
      }
      throw new Error(`HTTP ${response.responseCode}`);
    } finally {
      request.destroy();
    }
  }
}
