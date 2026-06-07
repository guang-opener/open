/**
 * WallpaperSync — 连接PC服务页面
 */
import { router } from '@kit.ArkUI';
import { ApiClient } from '../services/ApiClient';
import { ServerStatus } from '../models/WallpaperItem';
import { preferences } from '@kit.ArkData';
import { scanBarcode, scanCore } from '@kit.ScanKit';
import { BusinessError } from '@kit.BasicServicesKit';

const PREFS_NAME = 'wallpaper_sync_prefs';
const KEY_HOST_HISTORY = 'host_history';

@Entry
@Component
struct ConnectPage {
  @State serverHost: string = '';
  @State serverPort: string = '18920';
  @State isLoading: boolean = false;
  @State statusMessage: string = '';
  @State isConnected: boolean = false;
  @State hostHistory: string[] = [];
  @State isScanning: boolean = false;
  private apiClient: ApiClient | null = null;

  async aboutToAppear(): Promise<void> {
    await this.loadHistory();
  }

  async loadHistory(): Promise<void> {
    try {
      const dataPrefs = await preferences.getPreferences(
        AppStorage.get('context') as Context,
        PREFS_NAME
      );
      const json = (await dataPrefs.get(KEY_HOST_HISTORY, '[]')) as string;
      this.hostHistory = JSON.parse(json) as string[];
      if (this.hostHistory.length > 0 && !this.serverHost) {
        const last = this.hostHistory[0];
        const parts = last.split(':');
        this.serverHost = parts[0] || '';
        if (parts.length > 1) {
          this.serverPort = parts[1];
        }
      }
    } catch (_e) {
      this.hostHistory = [];
    }
  }

  async saveHistory(host: string): Promise<void> {
    const filtered = this.hostHistory.filter(h => h !== host);
    filtered.unshift(host);
    const trimmed = filtered.slice(0, 10);
    this.hostHistory = trimmed;
    try {
      const dataPrefs = await preferences.getPreferences(
        AppStorage.get('context') as Context,
        PREFS_NAME
      );
      await dataPrefs.put(KEY_HOST_HISTORY, JSON.stringify(trimmed));
      await dataPrefs.flush();
    } catch (_e) {
      // ignore
    }
  }

  async onConnect(): Promise<void> {
    if (!this.serverHost.trim()) {
      this.statusMessage = '请输入PC端IP地址';
      return;
    }
    this.isLoading = true;
    this.statusMessage = '正在连接...';
    this.isConnected = false;

    try {
      const url = `${this.serverHost.trim()}:${this.serverPort}`;
      this.apiClient = new ApiClient(url);
      const status = await this.apiClient.getStatus();
      if (status && status.ok) {
        this.isConnected = true;
        this.statusMessage = `连接成功！发现 ${status.totalWallpapers} 个壁纸`;
        await this.saveHistory(url);
        AppStorage.setOrCreate('apiClient', this.apiClient);
        AppStorage.setOrCreate('serverUrl', url);
        setTimeout(() => {
          router.pushUrl({ url: 'pages/RemoteBrowsePage' });
        }, 800);
      } else {
        this.statusMessage = '服务器返回异常';
      }
    } catch (e) {
      this.statusMessage = `连接失败: ${(e as Error).message}`;
      this.isConnected = false;
    } finally {
      this.isLoading = false;
    }
  }

  startScan(): void {
    this.isScanning = true;
    const options: scanBarcode.ScanOptions = {
      scanTypes: [scanCore.ScanType.QR_CODE],
    };
    try {
      scanBarcode.startScan(options).then((result: scanBarcode.ScanResult) => {
        this.isScanning = false;
        if (result && result.originalValue) {
          this.parseScanUrl(result.originalValue);
        }
      }).catch((err: BusinessError) => {
        this.isScanning = false;
        this.statusMessage = '扫码失败';
      });
    } catch (e) {
      this.isScanning = false;
      this.statusMessage = '扫码功能不可用';
    }
  }

  parseScanUrl(scannedUrl: string): void {
    try {
      let url = scannedUrl.trim();
      // 移除可能的 http:// 前缀再解析
      if (url.includes('://')) {
        let parts = url.split('://')[1];
        if (parts.includes(':')) {
          let hostAndPort = parts.split(':');
          this.serverHost = hostAndPort[0];
          this.serverPort = hostAndPort[1].split('/')[0];
        } else {
          this.serverHost = parts.split('/')[0];
        }
      } else {
        // 可能是 ip:port 格式
        if (url.includes(':')) {
          let parts = url.split(':');
          this.serverHost = parts[0];
          this.serverPort = parts[1].split('/')[0];
        } else {
          this.serverHost = url;
        }
      }
      this.statusMessage = '已扫描到地址，点击连接即可';
    } catch (e) {
      this.statusMessage = '无法解析二维码内容';
    }
  }

  onHistoryClick(host: string): void {
    const parts = host.split(':');
    this.serverHost = parts[0] || '';
    if (parts.length > 1) {
      this.serverPort = parts[1];
    }
    this.onConnect();
  }

  build() {
    Column() {
      Column() {
        Text('Wallpaper同步壁纸')
          .fontSize(28)
          .fontWeight(FontWeight.Bold)
          .fontColor('#FFFFFF')
          .margin({ bottom: 8 })
        Text('连接PC端Wallpaper Engine服务')
          .fontSize(14)
          .fontColor('#888888')
      }
      .alignItems(HorizontalAlign.Center)
      .margin({ top: 80, bottom: 40 })

      Column() {
        Text('PC 服务器地址')
          .fontSize(13)
          .fontColor('#BBBBBB')
          .margin({ bottom: 8 })
          .alignSelf(ItemAlign.Start)

        Row() {
          TextInput({ placeholder: '例如 192.168.1.100', text: this.serverHost })
            .layoutWeight(1)
            .height(48)
            .fontSize(16)
            .fontColor('#FFFFFF')
            .placeholderColor('#777777')
            .backgroundColor('#333333')
            .borderRadius(10)
            .borderColor('#555555')
            .borderWidth(1)
            .padding({ left: 14, right: 14 })
            .onChange((value: string) => { this.serverHost = value; })
          Text(' : ').fontSize(18).fontColor('#888')
          TextInput({ placeholder: '18920', text: this.serverPort })
            .width(80)
            .height(48)
            .fontSize(16)
            .fontColor('#FFFFFF')
            .placeholderColor('#777777')
            .type(InputType.Number)
            .backgroundColor('#333333')
            .borderRadius(10)
            .borderColor('#555555')
            .borderWidth(1)
            .padding({ left: 14, right: 14 })
            .onChange((value: string) => { this.serverPort = value; })
        }
        .width('100%')
      }
      .width('90%')
      .margin({ bottom: 12 })

      // 扫码按钮
      Button() {
        Row() {
          Text(this.isScanning ? '扫描中...' : '扫码连接').fontSize(14).fontColor('#FFFFFF')
        }
      }
      .width('90%').height(44)
      .backgroundColor('#FF8C00').borderRadius(10)
      .margin({ bottom: 8 })
      .onClick(() => { this.startScan(); })

      Button(this.isLoading ? '连接中...' : '连接服务器')
        .width('90%')
        .height(50)
        .fontSize(16)
        .backgroundColor(this.isLoading ? '#2E7D32' : '#4CAF50')
        .borderRadius(10)
        .enabled(!this.isLoading)
        .onClick(() => { this.onConnect(); })

      if (this.statusMessage) {
        Text(this.statusMessage)
          .fontSize(13)
          .fontColor(this.isConnected ? '#4CAF50' : '#FF8A80')
          .width('85%')
          .textAlign(TextAlign.Center)
          .margin({ top: 16 })
      }

      if (this.hostHistory.length > 0) {
        Column() {
          Text('连接历史')
            .fontSize(14)
            .fontColor('#BBBBBB')
            .margin({ top: 30, bottom: 10 })
            .alignSelf(ItemAlign.Start)

          ForEach(this.hostHistory, (host: string) => {
            Row() {
              Text(host)
                .fontSize(14)
                .fontColor('#DDDDDD')
                .layoutWeight(1)
              Text('连接')
                .fontSize(12)
                .fontColor('#4CAF50')
            }
            .width('100%')
            .height(44)
            .padding({ left: 14, right: 14 })
            .backgroundColor('#2A2A2A')
            .borderRadius(8)
            .margin({ bottom: 6 })
            .onClick(() => { this.onHistoryClick(host); })
          })
        }
        .width('90%')
      }

      Blank()

      Text('请确保手机和PC连接在同一WiFi网络')
        .fontSize(11)
        .fontColor('#666666')
        .margin({ bottom: 20 })
    }
    .width('100%')
    .height('100%')
    .backgroundColor('#0F0F0F')
  }
}
