/**
 * WallpaperSync — 壁纸保存服务
 */
import { fileIo } from '@kit.CoreFileKit';
import { http } from '@kit.NetworkKit';
import { photoAccessHelper } from '@kit.MediaLibraryKit';
import { common } from '@kit.AbilityKit';
import { abilityAccessCtrl, Permissions } from '@kit.AbilityKit';

const REQUIRED_PERMISSION: Permissions = 'ohos.permission.WRITE_IMAGEVIDEO';

async function requestPermission(): Promise<boolean> {
  const context = AppStorage.get('context') as common.UIAbilityContext;
  const atManager = abilityAccessCtrl.createAtManager();
  try {
    const grantStatus: abilityAccessCtrl.GrantStatus =
      await atManager.checkAccessToken(context.applicationInfo.accessTokenId, REQUIRED_PERMISSION);
    if (grantStatus === abilityAccessCtrl.GrantStatus.PERMISSION_GRANTED) {
      return true;
    }
    const result = await atManager.requestPermissionsFromUser(context, [REQUIRED_PERMISSION]);
    return result.authResults[0] === 0;
  } catch (_e) {
    return false;
  }
}

/** 普通保存视频到图库 */
export async function saveToGallery(videoPath: string): Promise<void> {
  const context = AppStorage.get('context') as common.UIAbilityContext;
  if (!await requestPermission()) throw new Error('请授予存储权限后重试');
  const helper = photoAccessHelper.getPhotoAccessHelper(context);
  const uri: string = await helper.createAsset(
    photoAccessHelper.PhotoType.VIDEO, 'mp4',
    { title: 'Wallpaper_' + Date.now(), subtype: photoAccessHelper.PhotoSubtype.DEFAULT }
  );
  _copyFile(videoPath, uri);
}

/** 保存为动态照片（预览图+视频合成），图库中可设为壁纸 */
export async function saveAsLivePhoto(previewUrl: string, videoPath: string): Promise<void> {
  const context = AppStorage.get('context') as common.UIAbilityContext;
  if (!await requestPermission()) throw new Error('请授予存储权限后重试');

  // 1. 下载预览图
  const imgReq = http.createHttp();
  let jpgBuf: ArrayBuffer = new ArrayBuffer(0);
  try {
    const resp = await imgReq.request(previewUrl, {
      method: http.RequestMethod.GET,
      connectTimeout: 10000,
      readTimeout: 30000,
      expectDataType: http.HttpDataType.ARRAY_BUFFER,
    });
    if (resp.responseCode !== 200) throw new Error('下载预览图失败');
    jpgBuf = resp.result as ArrayBuffer;
  } finally { imgReq.destroy(); }

  const jpgLen: number = jpgBuf.byteLength;
  const vidStat = fileIo.statSync(videoPath);
  const vidLen: number = vidStat.size;

  // 2. 在沙箱中创建临时合成文件
  const tmpDir: string = context.filesDir + '/wallpapers';
  if (!fileIo.accessSync(tmpDir)) { fileIo.mkdirSync(tmpDir, true); }
  const tmpPath: string = tmpDir + '/live_' + Date.now() + '.jpg';

  const outFile: fileIo.File = fileIo.openSync(tmpPath, fileIo.OpenMode.CREATE | fileIo.OpenMode.WRITE_ONLY);

  // 写入 JPEG 部分
  fileIo.writeSync(outFile.fd, jpgBuf);

  // 追加视频数据（分块读取）
  const vidFile: fileIo.File = fileIo.openSync(videoPath, fileIo.OpenMode.READ_ONLY);
  const vidChunk: ArrayBuffer = new ArrayBuffer(65536);
  let vidRead: number = fileIo.readSync(vidFile.fd, vidChunk);
  while (vidRead > 0) {
    if (vidRead < 65536) {
      fileIo.writeSync(outFile.fd, vidChunk.slice(0, vidRead) as ArrayBuffer);
    } else {
      fileIo.writeSync(outFile.fd, vidChunk);
    }
    vidRead = fileIo.readSync(vidFile.fd, vidChunk);
  }
  fileIo.closeSync(vidFile);

  // 写入 trailer: offset(4 LE) + length(4 LE) + "HUAWEI_LIVE" + 4 zero bytes
  const trailer: ArrayBuffer = new ArrayBuffer(20);
  const tv: Uint8Array = new Uint8Array(trailer);
  tv[0] = jpgLen & 0xFF; tv[1] = (jpgLen >>> 8) & 0xFF;
  tv[2] = (jpgLen >>> 16) & 0xFF; tv[3] = (jpgLen >>> 24) & 0xFF;
  tv[4] = vidLen & 0xFF; tv[5] = (vidLen >>> 8) & 0xFF;
  tv[6] = (vidLen >>> 16) & 0xFF; tv[7] = (vidLen >>> 24) & 0xFF;
  for (let i = 0; i < 12; i++) {
    tv[8 + i] = i < 11 ? "HUAWEI_LIVE".charCodeAt(i) : 0;
  }
  fileIo.writeSync(outFile.fd, trailer);
  fileIo.closeSync(outFile);

  // 3. 保存为图片到图库
  const helper = photoAccessHelper.getPhotoAccessHelper(context);
  const uri: string = await helper.createAsset(
    photoAccessHelper.PhotoType.IMAGE, 'jpg',
    { title: 'LiveWP_' + Date.now(), subtype: photoAccessHelper.PhotoSubtype.MOVING_PHOTO }
  );
  _copyFile(tmpPath, uri);
  fileIo.unlinkSync(tmpPath);
}

function _copyFile(src: string, dst: string): void {
  const dstFile: fileIo.File = fileIo.openSync(dst, fileIo.OpenMode.WRITE_ONLY);
  const srcFile: fileIo.File = fileIo.openSync(src, fileIo.OpenMode.READ_ONLY);
  const buf: ArrayBuffer = new ArrayBuffer(65536);
  let len: number = fileIo.readSync(srcFile.fd, buf);
  while (len > 0) {
    fileIo.writeSync(dstFile.fd, buf.slice(0, len) as ArrayBuffer);
    len = fileIo.readSync(srcFile.fd, buf);
  }
  fileIo.closeSync(srcFile);
  fileIo.closeSync(dstFile);
}
