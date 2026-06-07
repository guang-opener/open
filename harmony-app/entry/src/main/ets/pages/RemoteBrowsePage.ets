/**
 * WallpaperSync — 远程浏览PC壁纸页面
 */
import { router } from '@kit.ArkUI';
import { ApiClient } from '../services/ApiClient';
import { RemoteWallpaperItem, WallpaperListResponse } from '../models/WallpaperItem';
@Entry
@Component
struct RemoteBrowsePage {
  @State wallpapers: RemoteWallpaperItem[] = [];
  @State isLoading: boolean = true;
  @State currentPage: number = 1;
  @State hasMore: boolean = true;
  @State typeFilter: string = '';
  @State searchKeyword: string = '';
  @State searchInput: string = '';
  @State totalCount: number = 0;
  @State isRefreshing: boolean = false;
  @State ratingFilter: string = 'Everyone';
  private apiClient: ApiClient | null = null;

  aboutToAppear(): void {
    this.apiClient = AppStorage.get('apiClient') as ApiClient;
    this.loadWallpapers();
  }

  async loadWallpapers(isRefresh: boolean = false): Promise<void> {
    if (!this.apiClient) { return; }
    if (isRefresh) {
      this.currentPage = 1;
      this.hasMore = true;
      await this.apiClient.refreshServer();
    }
    this.isLoading = true;
    try {
      const result: WallpaperListResponse = await this.apiClient.getWallpapers(
        this.currentPage, 50, this.typeFilter, this.searchKeyword
      );
      let displayItems = result.items;
      // 本地过滤年龄分级
      if (this.ratingFilter) {
        displayItems = displayItems.filter(w => w.contentRating === this.ratingFilter);
      }
      if (this.currentPage === 1) {
        this.wallpapers = displayItems;
      } else {
        const existingIds = new Set(this.wallpapers.map(w => w.id));
        const newItems = displayItems.filter(w => !existingIds.has(w.id));
        this.wallpapers = this.wallpapers.concat(newItems);
      }
      this.totalCount = this.ratingFilter ? this.wallpapers.length : result.total;
      this.hasMore = result.hasMore;
    } catch (e) {
      console.error('加载失败:', (e as Error).message);
    } finally {
      this.isLoading = false;
    }
  }

  onRefresh(): void { this.loadWallpapers(true); }

  onLoadMore(): void {
    if (this.hasMore && !this.isLoading) {
      this.currentPage++;
      this.loadWallpapers();
    }
  }

  onFilterChange(filter: string): void {
    this.typeFilter = filter;
    this.currentPage = 1;
    this.hasMore = true;
    this.loadWallpapers();
  }

  onSearch(): void {
    this.searchKeyword = this.searchInput;
    this.currentPage = 1;
    this.hasMore = true;
    this.loadWallpapers();
  }

  onWallpaperClick(item: RemoteWallpaperItem): void {
    AppStorage.setOrCreate('currentWallpaper', item);
    router.pushUrl({ url: 'pages/PreviewPage' });
  }

  onGoToLocal(): void {
    router.pushUrl({ url: 'pages/LocalLibraryPage' });
  }

  build() {
    Column() {
      Row() {
        Text('远程壁纸')
          .fontSize(20).fontWeight(FontWeight.Bold).fontColor('#FFFFFF')
        Blank()
        Text(`共${this.totalCount}个`)
          .fontSize(12).fontColor('#888888').margin({ right: 12 })
        Button('本地库')
          .fontSize(12).height(32).backgroundColor('#1E1E1E').borderRadius(6)
          .onClick(() => { this.onGoToLocal(); })
      }
      .width('95%').margin({ top: 12, bottom: 8 })

      Row() {
        TextInput({ placeholder: '搜索壁纸...', text: this.searchInput })
          .layoutWeight(1).height(36).fontSize(13)
          .backgroundColor('#1E1E1E').borderRadius(8)
          .onChange((value: string) => { this.searchInput = value; })
          .onSubmit(() => { this.onSearch(); })
        Button('搜索')
          .fontSize(12).height(36).backgroundColor('#333').borderRadius(8)
          .margin({ left: 6 }).onClick(() => { this.onSearch(); })
      }
      .width('95%').margin({ bottom: 8 })

      Row() {
        ForEach(['全部', '视频', '场景'], (label: string, index: number) => {
          Text(label)
            .fontSize(12).padding({ left: 14, right: 14, top: 6, bottom: 6 })
            .backgroundColor(this.typeFilter === ['', 'video', 'scene'][index] ? '#4CAF50' : '#1E1E1E')
            .fontColor(this.typeFilter === ['', 'video', 'scene'][index] ? '#FFFFFF' : '#AAAAAA')
            .borderRadius(14).margin({ right: 8 })
            .onClick(() => { this.onFilterChange(['', 'video', 'scene'][index]); })
        })
      }
      .width('95%').margin({ bottom: 8 })

      Row() {
        ForEach(['不限', '全年龄', '成人'], (label: string, index: number) => {
          Text(label)
            .fontSize(11).padding({ left: 12, right: 12, top: 5, bottom: 5 })
            .backgroundColor(this.ratingFilter === ['', 'Everyone', 'Mature'][index] ? '#FF8C00' : '#1E1E1E')
            .fontColor(this.ratingFilter === ['', 'Everyone', 'Mature'][index] ? '#FFFFFF' : '#AAAAAA')
            .borderRadius(14).margin({ right: 6 })
            .onClick(() => {
              this.ratingFilter = ['', 'Everyone', 'Mature'][index];
              this.wallpapers = [];
              this.currentPage = 1;
              this.loadWallpapers(false);
            })
        })
      }
      .width('95%').margin({ bottom: 8 })

      Refresh({ refreshing: $$this.isRefreshing }) {
        if (this.isLoading && this.wallpapers.length === 0) {
          Column() {
            LoadingProgress().width(40).height(40).color('#4CAF50')
            Text('加载中...').fontSize(13).fontColor('#888').margin({ top: 10 })
          }
          .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
        } else if (this.wallpapers.length === 0) {
          Column() {
            Text('没有找到壁纸').fontSize(15).fontColor('#888')
          }
          .width('100%').layoutWeight(1).justifyContent(FlexAlign.Center)
        } else {
          Grid() {
            ForEach(this.wallpapers, (item: RemoteWallpaperItem) => {
              GridItem() {
                Column() {
                  Image(item.previewUrl)
                      .width('100%').aspectRatio(16 / 10)
                      .objectFit(ImageFit.Cover).backgroundColor('#1E1E1E')
                      .borderRadius({ topLeft: 10, topRight: 10 })
                    Column() {
                      Text(item.name)
                        .fontSize(12).fontColor('#DDDDDD').maxLines(1)
                        .textOverflow({ overflow: TextOverflow.Ellipsis })
                      Row() {
                        Text(item.type === 'video' ? '视频' : (item.type === 'scene' ? '场景' : '网页'))
                          .fontSize(10)
                          .fontColor(item.type === 'video' ? '#4CAF50' : '#FF9800')
                        if (item.contentRating === 'Mature') {
                          Text('18+')
                            .fontSize(9).fontColor('#FF5252')
                            .backgroundColor('#33FF5252').borderRadius(4)
                            .padding({ left: 4, right: 4, top: 1, bottom: 1 })
                            .margin({ left: 4 })
                        }
                        Blank()
                        if (item.sizeBytes > 0) {
                          Text(item.sizeBytes < 1048576 ? (item.sizeBytes / 1024).toFixed(0) + 'KB' : (item.sizeBytes / 1048576).toFixed(1) + 'MB')
                            .fontSize(10).fontColor('#666666')
                        }
                      }
                      .width('100%').margin({ top: 4 })
                    }
                    .padding({ left: 8, right: 8, top: 6, bottom: 8 })
                  }
                  .width('100%').backgroundColor('#1A1A1A').borderRadius(10)
                  .onClick(() => { this.onWallpaperClick(item); })
                }
            })
          }
          .columnsTemplate('1fr 1fr').columnsGap(10).rowsGap(10)
          .width('95%').layoutWeight(1)
          .onScrollIndex((first: number, last: number) => {
            if (last >= this.wallpapers.length - 4) { this.onLoadMore(); }
          })
        }
      }
      .onRefreshing(() => {
        this.isRefreshing = true;
        this.loadWallpapers(true).then(() => {
          this.isRefreshing = false;
        });
      })
    }
    .width('100%').height('100%').backgroundColor('#0F0F0F')
  }
}
