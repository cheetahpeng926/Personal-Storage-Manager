<div align="center">

# 📦 Personal Storage Manager

**Personal Inventory Management System**

Manage clothing, shoes, electronics, scale models and more — with image preview and Excel export

</div>

---

## ✨ Features

- **9 Categories**: T-Shirts, Long Sleeves, Shorts, Trousers, Socks, Shoes, Car Models, Driving Experience, Electronics
- **CRUD Operations**: Popup form input, required field validation, automatic date and scale formatting
- **Fuzzy Search**: Real-time filtering by brand, model, and other text fields
- **Column Sorting**: Click headers to cycle through ascending ▲, descending ▼, and default ↕
- **Image Management**: Add / replace / delete images per record, live preview in side panel, click to open with system viewer
- **Excel Export**: One-click export of all categories to Excel (one sheet per category)
- **Window Memory**: Automatically saves and restores last window position
- **Apple-inspired Clean UI**: Rounded buttons, custom oval scrollbar, light theme

## 🛠️ Tech Stack

| Component | Technology |
| --------- | ---------- |
| Language | Python 3.8+ |
| GUI | tkinter + ttk |
| Database | SQLite 3 (zero-config, single-file `data.db`) |
| Image Processing | Pillow |
| Excel Export | openpyxl (optional) |

## 📁 Project Structure

```
├── main.py              # Entry point
├── app.py               # Main application (GUI + business logic)
├── db.py                # Database setup and connection
├── config.py            # Database configuration
├── requirements.txt     # Python dependencies
├── Personal Storage Manager.spec  # PyInstaller build config
├── Pictures/            # Image storage directory (auto-created)
│   ├── short-sleeve pic/
│   ├── long-sleeve pic/
│   ├── shorts pic/
│   ├── trousers pic/
│   ├── socks pic/
│   ├── shoes pic/
│   ├── models pic/
│   ├── driving pic/
│   └── electronics pic/
└── .window_pos.json     # Window position cache (auto-generated)
```

---

## 🚀 Quick Start

### 1. Requirements

- Python 3.8+
- Optional: [MiSans](https://hyperos.mi.com/font/download) font (falls back to system Heiti if missing)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

For Excel export support, additionally install:

```bash
pip install openpyxl
```

### 3. Launch

**Windows Portable Version**

Go to [Releases](https://github.com/cheetahpeng926/Personal-Storage-Manager/releases), download `Personal Storage Manager.exe`, place it in an empty folder, and double-click to run.

**Or run from source**

```bash
python main.py
```

On first launch, the `data.db` database and all nine tables are created automatically in the same directory. **No database configuration needed.**

---

## 📊 Data Tables

| Category | Fields |
| :------: | :----- |
| 👕 T-Shirt / <br>🧥 Long Sleeve | Brand, Model, Color, Article No., Length, Chest, Shoulder, Size, Purchase Date |
| 🩳 Shorts / <br>👖 Trousers | Brand, Model, Color, Article No., Length, Waist, Hip, Size, Purchase Date |
| 🧦 Socks | Brand, Model, Color, Article No., Size, Purchase Date |
| 👟 Shoes | Brand, Model, Color, Article No., mm, EUR, Purchase Date |
| 🚗 Car Models | Scale, Real Brand/Model, Color, Model Brand, Purchase Date |
| 🏎️ Driving Experience | Year, Model, Version, Drivetrain |
| 📱 Electronics | Category (Phone/Tablet/Watch/Earbuds), Brand, Model, Color, Release Date, Purchase Date, Status |

## 💡 Tips

- **Date format**: Supports `YYYY.MM.DD`; pasting 8 digits auto-inserts dots (`20240315` → `2024.03.15`)
- **Scale field**: Full-width colons auto-convert to ASCII (`1：18` → `1:18`)
- **Image formats**: JPG / PNG / GIF / BMP / WEBP
- **Column sorting**: Click headers to cycle → Ascending ▲ → Descending ▼ → Default
- **Export**: Click the "Export" button at the bottom-left to generate a formatted Excel file
- **Double-click to edit**: Double-click any table row to open the edit form

## ⚠️ Notes

- Data is stored in `data.db` in the same directory — remember to back it up
- Images are stored in `Pictures/` subdirectories by category
- Deleting a record also removes its associated image file
- Designed for local use; modify as needed for remote access
