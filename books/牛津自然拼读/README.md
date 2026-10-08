# Oxford Phonics 点读书

本地离线阅读 Oxford Phonics World 3 Student Book，点击书上的 Disc / Track 图标播放音频。

## 使用

电脑需要 Node.js 18 或以上。双击 `start.cmd`，在浏览器中打开 http://127.0.0.1:4173 。保持启动窗口运行；关闭窗口即停止服务。也可执行 `npm start`。

- 点击绿色圆形音频标记，底部出现播放器：后退 5 秒、播放/暂停、前进 5 秒。
- 桌面宽屏还显示可拖动的音频进度条。
- 页码指 PDF 实际页序（例如 PDF 第 5 页是教材印刷第 4 页）。支持直接输入页码、翻页、缩放和记住上次阅读位置。
- 左右方向键翻页；播放器打开时，空格控制播放/暂停。
- 点击“调整音频区域”，选 Disc 和 Track 后在图标上拖出矩形。点击现有区域可删除；“恢复本页初始区域”撤销本页修改。
- 区域修改保存在当前浏览器。点击“导出坐标”，用下载的 `book.json` 替换 `public/book.json`，即可把修改纳入仓库。

## 项目结构

- `public/index.html`、`style.css`、`app.js`：不依赖第三方前端库的阅读器。
- `public/book.json`：教材页序、音频索引和归一化点击区域坐标，是后续维护的主要数据文件。
- `public/book.pdf`：原始 PDF；`public/pages/`：PDF 高清页面渲染。阅读器将这些页面内嵌显示，让点击区域随页面缩放保持对齐。
- `public/audio/`：规范命名的本地 MP3。根据文件名中的 Disc 编号识别，不根据文件夹推断；原 Disc 2 文件夹内重复的 Disc 1 Track 68 会去重。
- `server.js`：仅监听本机的静态服务，支持音频 Range 请求以便跳转。
- `scripts/prepare.py`：从项目上一级目录重新导入本地 PDF 和音频，保留已有音频坐标。
- `tests/reader.test.js`：资源引用、区域边界、音频范围请求测试。

## 重新生成资源

常规使用不需要 Python。只有重新导入资源时才需要 Python 及 PyMuPDF：

```sh
python -m pip install pymupdf
python scripts/prepare.py
npm test
```

默认从项目上一级寻找 `*3 Student*.pdf` 和 `oxford-phonics-world-level3-disc*`。所有媒体已复制到本项目，日常使用无需保留原路径。程序和坐标可放入 Git 仓库；较大的教材 PDF、渲染页面、MP3 和本地 Python 依赖已在 `.gitignore` 中排除，换电脑时另行复制 `public` 下的媒体目录和 PDF。

当前版本为本地网页应用，不是 Windows 安装包。无需网络服务、账号或云端上传。

## 本册核对结果

105 个 PDF 页面、133 处已核对音频区域、136 个独立 MP3。点击区域覆盖 Disc 1 Track 03–68、Disc 2 Track 02–68；其余 Disc 1 Track 01/02 和 Disc 2 Track 01 可通过“全部音频”播放。曲目编号与图标已逐一核对，播放交互已抽样验证，并未逐段听完全部音频内容。

## 侧边目录

按书中两页目录还原 8 个 Unit、4 个 Review、Picture Dictionary、Student Cards 和 Certificate，保留拼读组合、例词及 Story / Song / Game 入口。点击单元标题跳转，旁边箭头展开或收起详细内容；当前章节自动高亮。窄窗口点击右上角“目录”打开侧栏。

目录数据位于 `public/contents.js`，页码使用书本印刷页码；本扫描版的 PDF 页序为印刷页码加 1。
