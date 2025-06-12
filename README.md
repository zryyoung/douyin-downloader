# 📲 Douyin Downloader 安卓版

本项目基于 [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader) Fork 改造，重新构建为一个 **无需依赖、可直接在 Android 手机上运行的抖音批量视频下载 App**。

---

## ✨ 项目亮点

- ✅ 采用 **Java + Python** 构建，**Chaquopy** 插件结合，原生 Android App，脱离 PC 端使用，无需其他依赖，APP独立运行
- ✅ 支持**多个作者主页链接批量导入**
- ✅ 支持**多线程高速下载**
- ✅ 内置数据库，**自动跳过已下载内容，避免重复**
- ✅ 不填 Cookie 也支持批量下载，只是下载的不全，只有最新的少数视频，用户**手动填写 Cookie**，可下载主页所有视频
- ✅ 使用 SDK 36 编译，兼容 Android 6.0 ~ Android 14+

---

## 📥 使用方法

1. 在浏览器中访问作者主页，打开开发者工具或使用抓包工具，获取抖音网页版 Cookie，手机端可以通过kiwi浏览器获取 Cookie
2. 将主页链接与 Cookie 粘贴到 App 中对应输入框
3. 可一次性粘贴多个作者主页链接（换行分隔）
4. 开始下载，应用将并发下载作者的全部公开作品

---

## 🧠 防重复机制

App 会自动将已下载作品记录进数据库，在后续操作中跳过，避免重复下载、节省流量和存储空间。

---

## ⚙️ 技术参数

- 编译环境：Android SDK 36
- 目标兼容：Android 6.0（API 23）起
- 构建方式：支持 Termux / ZeroTermux 本地构建
- 下载机制：多线程并发，稳定可靠

---

## 🧪 Termux 构建方式（可选）

如需本地构建 APK：

```bash
pkg update && pkg install openjdk-17 git unzip -y # Android sdk 自行下载安装可参考openjdk-Temrux的项目仓库
git clone https://github.com/zryyoung/douyin-downloader.git
cd douyin-downloader
# 自行修改配置文件后编译
gradle assembleDebug
```

APK 输出路径：
```
app/build/outputs/apk/debug/app-debug.apk
```

---

## 🙏 致谢

感谢 [jiji262/douyin-downloader](https://github.com/jiji262/douyin-downloader) 的原始命令行版本，提供了极大的参考价值。

---

## 📝 License

本项目仅用于学习交流，不得用于商业或违法用途。