/**
 * WallpaperSync — 壁纸预览页面
 */
import { router } from '@kit.ArkUI';
import { promptAction } from '@kit.ArkUI';
import { RemoteWallpaperItem, LocalWallpaperItem } from '../models/WallpaperItem';
import { ApiClient } from '../services/ApiClient';
import { downloadWallpaper } from '../services/DownloadManager';
import { saveToGallery, saveAsLivePhoto } from '../services/WallpaperService';

@Entry
@Component
struct PreviewPage {
  @State wallpaperName: string = '';
  @State wallpaperAuthor: string = '';
  @State wallpaperType: string = '';
  @State previewUrl: string = '';
  @State downloadUrl: string = '';
  @State wallpaperId: string = '';
  @State isFromLocal: boolean = false;
  @State localVideoPath: string = '';
  @State isDownloading: boolean = false;
  @State downloadPercent: number = 0;
  @State isDownloaded: boolean = false;
  @State isSaving: boolean = false;

  aboutToAppear(): void {
    const remoteItem = AppStorage.get('currentWallpaper') as RemoteWallpaperItem;
    const localItem = AppStorage.get('localWallpaperItem') as LocalWallpaperItem;

    if (localItem) {
      this.isFromLocal = true;
      this.wallpaperName = localItem.name;
      this.wallpaperId = localItem.id;
      this.localVideoPath = localItem.localPath;
      this.isDownloaded = true;
      this.wallpaperType = 'video';
    } else if (remoteItem) {
      this.isFromLocal = false;
      this.wallpaperName = remoteItem.name;
      this.wallpaperAuthor = remoteItem.author;
      this.wallpaperType = remoteItem.type;
      this.previewUrl = remoteItem.previewUrl;
      this.downloadUrl = remoteItem.downloadUrl;
      this.wallpaperId = remoteItem.id;
    }
  }

  async onDownload(): Promise<void> {
    if (this.isDownloaded || this.isDownloading) { return; }
    this.isDownloading = true;
    this.downloadPercent = 0;
    try {
      const apiClient = AppStorage.get('apiClient') as ApiClient;
      if (!apiClient) {
        promptAction.showToast({ message: '未连接到服务器' });
        return;
      }
      const url = apiClient.getDownloadUrl(this.wallpaperId);
      const localPath = await downloadWallpaper(url, this.wallpaperId, this.wallpaperName,
        (percent: number) => { this.downloadPercent = percent; });
      this.localVideoPath = localPath;
      this.isDownloaded = true;
      promptAction.showToast({ message: '下载完成！' });
    } catch (e) {
      promptAction.showToast({ message: `下载失败: ${(e as Error).message}` });
    } finally {
      this.isDownloading = false;
    }
  }

  async onSaveToGallery(): Promise<void> {
    if (!this.isDownloaded || this.isSaving) { return; }
    this.isSaving = true;
    try {
      await saveToGallery(this.localVideoPath);
      promptAction.showToast({ message: '已保存到图库！打开图库即可设为动态壁纸' });
    } catch (e) {
      promptAction.showToast({ message: '已下载完成，请打开图库选择视频设为壁纸' });
    } finally {
      this.isSaving = false;
    }
  }

  build() {
    Column() {
      Row() {
        Button() {
          Text('<').fontSize(18).fontColor('#FFFFFF')
        }
        .width(36).height(36).backgroundColor('#1E1E1E').borderRadius(8)
        .onClick(() => { router.back(); })
        Text('预览').fontSize(20).fontWeight(FontWeight.Bold).fontColor('#FFFFFF').margin({ left: 12 })
      }
      .width('95%').margin({ top: 12, bottom: 12 })

      Column() {
        if (this.wallpaperType === 'video' && this.isDownloaded) {
          Video({ src: 'file://' + this.localVideoPath, controller: new VideoController() })
            .width('100%').aspectRatio(16 / 9).objectFit(ImageFit.Contain)
            .autoPlay(true).loop(true).controls(true)
            .backgroundColor('#000000').borderRadius(12)
        } else if (this.wallpaperType === 'video' && !this.isDownloaded) {
          Stack() {
            Image(this.previewUrl)
              .width('100%').aspectRatio(16 / 9).objectFit(ImageFit.Cover).borderRadius(12)
            Column() {
              Text('下载后可预览视频').fontSize(13).fontColor('#CCCCCC')
            }
            .alignItems(HorizontalAlign.Center)
          }
          .width('100%')
        } else if (this.wallpaperType === 'scene') {
          Stack() {
            Image(this.previewUrl)
              .width('100%').aspectRatio(16 / 9).objectFit(ImageFit.Cover).borderRadius(12)
            Column() {
              Text('场景壁纸').fontSize(16).fontColor('#FFFFFF').fontWeight(FontWeight.Bold).margin({ bottom: 8 })
              Text('请在PC端Wallpaper Engine中录制为MP4再同步。')
                .fontSize(12).fontColor('#CCCCCC').textAlign(TextAlign.Center).width('80%')
            }
            .alignItems(HorizontalAlign.Center)
          }
          .width('100%')
        } else {
          Image(this.previewUrl)
            .width('100%').aspectRatio(16 / 9).objectFit(ImageFit.Cover).borderRadius(12)
        }
      }
      .width('92%').margin({ bottom: 16 })

      Column() {
        Text(this.wallpaperName).fontSize(18).fontWeight(FontWeight.Medium).fontColor('#FFFFFF').margin({ bottom: 4 })
        if (this.wallpaperAuthor) {
          Text(`作者: ${this.wallpaperAuthor}`).fontSize(12).fontColor('#888888')
        }
      }
      .alignItems(HorizontalAlign.Center).margin({ bottom: 20 })

      if (this.isDownloading) {
        Column() {
          Progress({ value: this.downloadPercent, total: 100, type: ProgressType.Linear })
            .width('90%').height(4).color('#4CAF50')
          Text(`下载中 ${this.downloadPercent}%`).fontSize(12).fontColor('#888888').margin({ top: 6 })
        }
        .margin({ bottom: 16 })
      }

      if (this.wallpaperType === 'video') {
        if (!this.isDownloaded) {
          Button(this.isDownloading ? `下载中 ${this.downloadPercent}%` : '下载到本地')
            .width('90%').height(48).fontSize(15)
            .backgroundColor(this.isDownloading ? '#333333' : '#4CAF50').borderRadius(10)
            .enabled(!this.isDownloading).onClick(() => { this.onDownload(); })
            .margin({ bottom: 12 })
        } else {
          Button(this.isSaving ? '保存中...' : '保存为动态照片（图库预览）')
            .width('90%').height(46).fontSize(14)
            .backgroundColor('#E65100').borderRadius(10)
            .enabled(!this.isSaving).onClick(() => {
              this.isSaving = true;
              saveAsLivePhoto(this.previewUrl, this.localVideoPath).then(() => {
                promptAction.showToast({ message: '已保存为动态照片！图库可预览动画' });
                this.isSaving = false;
              }).catch((e: Error) => {
                promptAction.showToast({ message: `失败: ${(e as Error).message}` });
                this.isSaving = false;
              });
            })
            .margin({ bottom: 8 })

          Button(this.isSaving ? '保存中...' : '保存为普通视频')
            .width('90%').height(42).fontSize(13)
            .backgroundColor('#333333').borderRadius(10)
            .enabled(!this.isSaving).onClick(() => { this.onSaveToGallery(); })
            .margin({ bottom: 6 })

          Text('注：鸿蒙6.0设壁纸时只取静态帧，动态效果仅图库可见')
            .fontSize(10).fontColor('#FF8A80')
            .textAlign(TextAlign.Center).width('85%')
        }
      }
    }
    .width('100%').height('100%').backgroundColor('#0F0F0F')
  }
}
