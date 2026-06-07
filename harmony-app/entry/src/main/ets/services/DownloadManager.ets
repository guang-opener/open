/**
 * WallpaperSync — 下载管理器
 */
import { request } from '@kit.BasicServicesKit';
import { fileIo } from '@kit.CoreFileKit';
import { preferences } from '@kit.ArkData';
import { common } from '@kit.AbilityKit';
import { LocalWallpaperItem } from '../models/WallpaperItem';

const PREFS_NAME = 'wallpaper_sync_prefs';
const PREFS_KEY_LOCAL_LIST = 'local_wallpapers';

export async function downloadWallpaper(
  url: string,
  wallpaperId: string,
  wallpaperName: string,
  onProgress?: (percent: number) => void
): Promise<string> {
  const context = AppStorage.get('context') as common.UIAbilityContext;
  const finalDir: string = context.filesDir + '/wallpapers';
  const ext = url.match(/\.(mp4|webm|mkv)/i)?.[0] ?? '.mp4';
  const fileName = `${wallpaperId}_${sanitizeFileName(wallpaperName)}${ext}`;
  const finalPath: string = finalDir + '/' + fileName;

  if (!fileIo.accessSync(finalDir)) {
    fileIo.mkdirSync(finalDir, true);
  }

  if (fileIo.accessSync(finalPath)) {
    if (onProgress) { onProgress(100); }
    addToLocalLibrary(wallpaperId, wallpaperName, finalPath);
    return finalPath;
  }

  // 使用 @ohos.request 下载
  const task: request.DownloadTask = await request.downloadFile(context, {
    url: url,
    filePath: finalPath,
    enableMetered: false,
    enableRoaming: false,
  });

  return new Promise<string>((resolve, reject) => {
    task.on('progress', (received: number, total: number) => {
      if (total > 0 && onProgress) {
        onProgress(Math.round((received / total) * 100));
      }
    });
    task.on('complete', () => {
      if (onProgress) { onProgress(100); }
      addToLocalLibrary(wallpaperId, wallpaperName, finalPath);
      resolve(finalPath);
    });
    task.on('fail', (code: number) => {
      reject(new Error(`下载失败，错误码: ${code}`));
    });
  });
}

export async function getLocalWallpapers(): Promise<LocalWallpaperItem[]> {
  try {
    const dataPreferences = await preferences.getPreferences(
      AppStorage.get('context') as Context,
      PREFS_NAME
    );
    const jsonStr = (await dataPreferences.get(PREFS_KEY_LOCAL_LIST, '[]')) as string;
    const arr = JSON.parse(jsonStr) as Array<Record<string, Object>>;
    return arr.map((item: Record<string, Object>) => {
      const w = new LocalWallpaperItem();
      w.id = (item['id'] as string) ?? '';
      w.name = (item['name'] as string) ?? '';
      w.author = (item['author'] as string) ?? '';
      w.localPath = (item['localPath'] as string) ?? '';
      w.sizeBytes = (item['sizeBytes'] as number) ?? 0;
      w.downloadTime = (item['downloadTime'] as number) ?? 0;
      return w;
    });
  } catch (_e) {
    return [];
  }
}

export async function deleteLocalWallpaper(wallpaperId: string): Promise<void> {
  const list = await getLocalWallpapers();
  const target = list.find(w => w.id === wallpaperId);
  if (target) {
    try {
      if (fileIo.accessSync(target.localPath)) {
        fileIo.unlinkSync(target.localPath);
      }
    } catch (_e) { /* ignore */ }
  }
  await _saveLocalList(list.filter(w => w.id !== wallpaperId));
}

async function addToLocalLibrary(id: string, name: string, localPath: string): Promise<void> {
  const list = await getLocalWallpapers();
  const existing = list.findIndex(w => w.id === id);
  const item = new LocalWallpaperItem();
  item.id = id;
  item.name = name;
  item.localPath = localPath;
  item.downloadTime = Date.now();
  try { item.sizeBytes = fileIo.statSync(localPath).size; } catch (_e) { /* ignore */ }
  if (existing >= 0) { list[existing] = item; }
  else { list.unshift(item); }
  await _saveLocalList(list);
}

async function _saveLocalList(list: LocalWallpaperItem[]): Promise<void> {
  const dp = await preferences.getPreferences(AppStorage.get('context') as Context, PREFS_NAME);
  const raw: Record<string, Object>[] = [];
  for (const w of list) {
    const si: Record<string, Object> = {
      'id': w.id, 'name': w.name, 'author': w.author,
      'localPath': w.localPath, 'sizeBytes': w.sizeBytes, 'downloadTime': w.downloadTime,
    };
    raw.push(si);
  }
  const arr: string = JSON.stringify(raw);
  await dp.put(PREFS_KEY_LOCAL_LIST, arr);
  await dp.flush();
}

function sanitizeFileName(name: string): string {
  return name.replace(/[\\/:*?"<>|]/g, '_').substring(0, 50);
}
