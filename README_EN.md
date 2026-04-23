<div align="center">

# 📦 Personal Storage Manager

**Personal Item Warehouse Management System**

Manage clothing, shoes, electronics, car models, and other personal items with image preview and ZIP backup

</div>

---

## ✨ Features

- **Nine Categories**: Short-sleeve, Long-sleeve, Shorts, Trousers, Socks, Shoes, Car Models, Driving Experience, Electronics
- **CRUD Operations**: Form-based entry with required field validation, auto-formatting for date and scale fields
- **Fuzzy Search**: Real-time filtering by brand, model, and other text fields (300ms debounce)
- **Column Sorting**: Click table headers to cycle through ascending ▲, descending ▼, and default ↕
- **Multi-select Mode**: Click "Multi-select" button to enter multi-select mode for batch deletion
- **Image Management**: Add/replace/delete images for each record with real-time preview in the right panel
- **ZIP Backup**: One-click export of data + images to ZIP file, automatic extraction on import
- **Import Deduplication**: Automatically detect and skip duplicate records (all fields must match)
- **Date Formats**: Supports `YYYY.MM.DD`, `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYYMMDD` input formats
- **Window Memory**: Automatically saves and restores window position and size
- **Apple-style Clean UI**: Rounded buttons, custom scrollbars, light theme

---

## 🛠️ Tech Stack

| Component  | Technology                            |
| :--------: | :-----------------------------------: |
| Language   | Python 3.8+                           |
| GUI        | Flet 0.84+ (Flutter framework)        |
| Database   | SQLite 3 (zero-config, single `data.db` file) |
| Image      | Pillow                                |
| Excel      | openpyxl (optional)                   |

---

## 📁 Project Structure

```
Personal Storage Manager/
├── main.py                              # Entry point, application state management
├── constants.py                         # Categories, fields, colors and other constants
├── db.py                                # Database schema and connection
├── services.py                          # Image management, import/export services
├── controllers.py                       # Controllers (dialogs, event handlers)
├── ui.py                                # UI rendering (layout, table, sidebar)
├── tests/
│   ├── test_all.py                      # Unified test file
│   └── _tmp/                            # Test temporary directory
├── requirements.txt                     # Python dependencies
├── Personal Storage Manager.spec        # PyInstaller config
├── PingFangSC-Regular.ttf               # Chinese font
├── SF-Pro-Text-Regular.otf               # English font
├── icon.ico                             # Application icon
├── Pictures/                            # Image storage directory (auto-created)
│   ├── short-sleeve pic/
│   ├── long-sleeve pic/
│   ├── shorts pic/
│   ├── trousers pic/
│   ├── socks pic/
│   ├── shoes pic/
│   ├── models pic/
│   ├── driving pic/
│   └── electronics pic/
├── data.db                              # Database file (auto-generated)
└── .window_pos.json                     # Window position cache (auto-generated)
```

---

## 🚀 Quick Start

### 1. Requirements

- Python 3.8+
- Optional: PingFang SC font (falls back to system default if missing)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

**Windows Standalone Version**

Download `Personal Storage Manager.exe` from [Releases](https://github.com/cheetahpeng926/Personal-Storage-Manager/releases), place it in an empty folder, and double-click to run.

**Or run from source**

```bash
python main.py
```

On first launch, `data.db` database and nine tables will be created automatically. **No database configuration required.**

---

## 📊 Data Tables

|        Category        |                                           Main Fields                                           |
| :--------------------: | :--------------------------------------------------------------------------------------------: |
| 👕 Short-sleeve / 🧥 Long-sleeve |      Brand, Model, Color, Article No., Length, Chest, Shoulder, Size, Purchase Date       |
|    🩳 Shorts / 👖 Trousers     |          Brand, Model, Color, Article No., Length, Waist, Hip, Size, Purchase Date          |
|        🧦 Socks        |                  Brand, Model, Color, Article No., Size, Purchase Date                   |
|        👟 Shoes        |                Brand, Model, Color, Article No., mm, EUR, Purchase Date                 |
|     🚗 Car Models      |           Scale, Real Brand/Model, Color, Model Brand, Purchase Date            |
|  🏎️ Driving Experiences  |                          Year, Model, Version, Drivetrain                           |
|     📱 Electronics     | Category, Brand, Model, Color, Release Date, Purchase Date, Status |

---

## 💡 Usage Tips

- **Date Format**: Supports `YYYY.MM.DD`, `YYYY-MM-DD`, `YYYY/MM/DD`, `YYYYMMDD`, stored as `YYYY.MM.DD`
- **Scale Field**: Chinese colon auto-converts to English (`1：18` → `1:18`)
- **Image Formats**: JPG / PNG / GIF / BMP / WEBP supported
- **Column Sorting**: Click header to cycle → Ascending ▲ → Descending ▼ → Default
- **Multi-select Mode**: Click "Multi-select" button to enter, click again to exit
- **Export**: Click "Export" button to generate ZIP file (Excel + images)
- **Import**: Click "Import" button to select ZIP file and restore data and images

---

## ⚠️ Notes

- Data is stored in `data.db` file in the same directory - remember to backup
- Images are automatically stored in `Pictures/` subdirectories by category
- Deleting a record also deletes the associated image file
- Import automatically skips completely duplicate records (all fields match)
- Designed for local use only; modify for remote access if needed
