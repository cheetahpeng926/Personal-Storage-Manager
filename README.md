<div align="center">

# 📦 Personal Storage Manager

**个人物品仓库管理系统**

管理衣物、鞋子、电子设备、汽车模型等个人物品，支持图片预览与 ZIP 备份。

</div>

---

## ✨ 功能特性

- **九大分类管理**：短袖、长袖、短裤、长裤、袜子、鞋子、汽车模型、驾驶经历、电子设备
- **增删改查**：弹出表单录入，必填校验，自动格式化日期与比例字段
- **模糊搜索**：按品牌、型号等文本字段实时过滤
- **列排序**：点击表头在升序 ▲、降序 ▼、默认 ↕ 之间循环切换
- **多选模式**：点击「多选」按钮进入多选模式，支持批量删除
- **图片管理**：每条记录支持添加 / 更换 / 删除图片，右侧面板实时预览
- **ZIP 备份**：一键导出数据 + 图片为 ZIP 文件，导入时自动解压恢复
- **导入去重**：导入时自动检测重复记录（所有字段一致则跳过）
- **日期格式**：支持 `YYYY.MM.DD`、`YYYY-MM-DD`、`YYYY/MM/DD`、`YYYYMMDD` 四种输入格式
- **窗口记忆**：自动保存并恢复上次窗口位置和大小
- **Apple 风格简洁 UI**：圆角按钮、自定义滚动条、浅色主题

---

## 🛠️ 技术栈

|    组件    |                技术                  |
| :--------: | :----------------------------------: |
|    语言    |             Python 3.8+              |
|    GUI     |      Flet 0.84+（Flutter 框架）      |
|   数据库   | SQLite 3（零配置，单文件 `data.db`） |
|  图片处理  |               Pillow                 |
| Excel 导出 |          openpyxl（可选）            |

---

## 📁 项目结构

```
Personal Storage Manager/
├── main.py                              # 启动入口，应用状态管理
├── constants.py                         # 分类、字段、配色等常量
├── db.py                                # 数据库建表与连接
├── services.py                          # 图片管理、导入导出服务
├── controllers.py                       # 控制器（对话框、事件处理）
├── ui.py                                # UI 渲染（布局、表格、侧边栏）
├── tests/
│   ├── test_all.py                      # 统一测试文件
│   └── _tmp/                            # 测试临时目录
├── requirements.txt                     # Python 依赖
├── Personal Storage Manager.spec        # PyInstaller 打包配置
├── PingFangSC-Regular.ttf               # 中文字体
├── SF-Pro-Text-Regular.otf               # 英文字体
├── icon.ico                             # 应用图标
├── Pictures/                            # 图片存储目录（自动创建）
│   ├── short-sleeve pic/
│   ├── long-sleeve pic/
│   ├── shorts pic/
│   ├── trousers pic/
│   ├── socks pic/
│   ├── shoes pic/
│   ├── models pic/
│   ├── driving pic/
│   └── electronics pic/
├── data.db                              # 数据库文件（自动生成）
└── .window_pos.json                     # 窗口位置缓存（自动生成）
```

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- 可选：PingFang SC 字体（缺失时自动回退到系统默认）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动

**Windows 免安装版**

前往 [Releases](https://github.com/cheetahpeng926/Personal-Storage-Manager/releases) 下载 Personal Storage Manager.exe 放在空文件夹中，直接双击即可使用

**或下载源码后执行**

```bash
python main.py
```

首次启动会在同目录自动创建 `data.db` 数据库及九张数据表，**无需任何数据库配置。**

---

## 📊 数据表一览

|        分类        |                    主要字段                    |
| :----------------: | :--------------------------------------------: |
| 👕 短袖 / 🧥 长袖 |  品牌、型号、配色、货号、衣长、胸围、肩宽、尺码、购买日期  |
| 🩳 短裤 / 👖 长裤 |  品牌、型号、配色、货号、裤长、腰围、臀围、尺码、购买日期  |
|      🧦 袜子      |          品牌、型号、配色、货号、尺码、购买日期          |
|      👟 鞋子      |        品牌、型号、配色、货号、mm、EUR、购买日期         |
|    🚗 汽车模型    |     比例、实车品牌/型号、配色、模型品牌、购买日期     |
|    🏎️ 驾驶经历    |            年份、型号、版本、驱动形式            |
|    📱 电子设备    | 类别、品牌、型号、配色、发布日期、购买日期、状态 |

---

## 💡 使用提示

- **日期格式**：支持 `YYYY.MM.DD`、`YYYY-MM-DD`、`YYYY/MM/DD`、`YYYYMMDD`，统一存储为 `YYYY.MM.DD`
- **比例字段**：中文冒号自动转英文（`1：18` → `1:18`）
- **图片格式**：支持 JPG / PNG / GIF / BMP / WEBP
- **列排序**：点击表头循环切换 → 升序 ▲ → 降序 ▼ → 默认
- **多选模式**：点击「多选」按钮进入多选模式，再次点击退出
- **导出**：点击左下角「导出」按钮，生成 ZIP 文件（包含 Excel + 图片）
- **导入**：点击「导入」按钮，选择 ZIP 文件自动恢复数据和图片

---

## ⚠️ 注意事项

- 数据存储在同目录的 `data.db` 文件中，注意备份
- 图片按分类自动存储在 `Pictures/` 子目录下
- 删除记录时会同步删除关联的图片文件
- 导入时会自动跳过完全重复的记录（所有字段一致）
- 默认仅支持本地使用，如需远程访问请自行改造
