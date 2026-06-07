/**
 * WallpaperSync — 本地壁纸库页面
 */
import { router } from '@kit.ArkUI';
import { LocalWallpaperItem } from '../models/WallpaperItem';
import { getLocalWallpapers, deleteLocalWallpaper } from '../services/DownloadManager';

@Entry
@Component
struct LocalLibraryPage {
  @State wallpapers: LocalWallpaperItem[] = [];
  @State isLoading: boolean = true;
  @State isEditMode: boolean = false;
  @State selectedIds: Set<string> = new Set();

  aboutToAppear(): void { this.loadData(); }
  onPageShow(): void { this.loadData(); }

  async loadData(): Promise<void> {
    this.isLoading = true;
    try { this.wallpapers = await getLocalWallpapers(); }
    catch (e) { console.error('加载失败:', (e as Error).message); }
    finally { this.isLoading = false; }
  }

  onWallpaperClick(item: LocalWallpaperItem): void {
    if (this.isEditMode) {
      if (this.selectedIds.has(item.id)) { this.selectedIds.delete(item.id); }
      else { this.selectedIds.add(item.id); }
      this.selectedIds = new Set(this.selectedIds);
      return;
    }
    AppStorage.setOrCreate('localWallpaperItem', item);
    router.pushUrl({ url: 'pages/PreviewPage' });
  }

  async onDeleteItem(item: LocalWallpaperItem): Promise<void> {
    await deleteLocalWallpaper(item.id);
    await this.loadData();
  }

  async onDeleteSelected(): Promise<void> {
    for (const id of this.selectedIds) { await deleteLocalWallpaper(id); }
    this.selectedIds.clear();
    this.isEditMode = false;
    await this.loadData();
  }

  build() {
    Column() {
      Row() {
        Button() {
          Text('<').fontSize(18).fontColor('#FFFFFF')
        }
        .width(36).height(36).backgroundColor('#1E1E1E').borderRadius(8)
        .onClick(() => { router.back(); })
        Text('本地壁纸库').fontSize(20).fontWeight(FontWeight.Bold).fontColor('#FFFFFF').margin({ left: 12 })
        Blank()
        if (this.wallpapers.length > 0) {
          Text(this.isEditMode ? '完成' : '编辑')
            .fontSize(14).fontColor('#4CAF50')
            .onClick(() => {
              this.isEditMode = !this.isEditMode;
              if (!this.isEditMode) { this.selectedIds.clear(); }
            })
        }
      }
      .width('95%').margin({ top: 12, bottom: 8 })

      if (this.isEditMode && this.selectedIds.size > 0) {
        Button(`删除选中 (${this.selectedIds.size})`)
          .width('95%').height(44).fontSize(14).backgroundColor('#D32F2F').borderRadius(8)
          .margin({ bottom: 8 }).onClick(() => { this.onDeleteSelected(); })
      }

      if (this.isLoading) {
        Column() { LoadingProgress().width(40).height(40).color('#4CAF50') }
          .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else if (this.wallpapers.length === 0) {
        Column() {
          Text('还没有下载壁纸').fontSize(15).fontColor('#888')
        }
        .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
      } else {
        Grid() {
          ForEach(this.wallpapers, (item: LocalWallpaperItem) => {
            GridItem() {
              Stack() {
                Column() {
                  Image('file://' + item.localPath)
                    .width('100%').aspectRatio(16 / 10)
                    .objectFit(ImageFit.Cover).backgroundColor('#1E1E1E')
                    .borderRadius({ topLeft: 10, topRight: 10 })
                  Column() {
                    Text(item.name).fontSize(12).fontColor('#DDDDDD').maxLines(1)
                      .textOverflow({ overflow: TextOverflow.Ellipsis })
                    Text(new Date(item.downloadTime).toLocaleDateString())
                      .fontSize(10).fontColor('#666666').margin({ top: 3 })
                  }
                  .padding({ left: 8, right: 8, top: 6, bottom: 8 })
                }
                .width('100%').backgroundColor('#1A1A1A').borderRadius(10)
                .onClick(() => { this.onWallpaperClick(item); })

                if (!this.isEditMode) {
                  Row() {
                    Text('X').fontSize(14).fontColor('#FF5252')
                  }
                  .width(30).height(30).backgroundColor('#33FF5252').borderRadius(15)
                  .justifyContent(FlexAlign.Center)
                  .position({ x: '100%', y: 0 }).translate({ x: -8, y: 8 })
                  .onClick(() => { this.onDeleteItem(item); })
                }
              }
              .width('100%')
            }
          })
        }
        .columnsTemplate('1fr 1fr').columnsGap(10).rowsGap(10)
        .width('95%').layoutWeight(1)
      }
    }
    .width('100%').height('100%').backgroundColor('#0F0F0F')
  }
}
