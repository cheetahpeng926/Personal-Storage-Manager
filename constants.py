# -*- coding: utf-8 -*-
"""Project constants, configuration, and schema definition."""

import os
import sys

# ------------------------------------------------------------------
# Path configuration (merged from config.py)
# ------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "data.db")
PICTURES_DIR = os.path.join(BASE_DIR, "Pictures")
WINDOW_POSITION_FILE = os.path.join(BASE_DIR, ".window_pos.json")
LOG_PATH = os.path.join(BASE_DIR, "psm.log")


def resolve_image_path(path):
    """Resolve an image path to absolute. Supports both relative and legacy absolute paths."""
    if not path:
        return None
    if os.path.isabs(path):
        return path
    return os.path.join(PICTURES_DIR, path)


# ------------------------------------------------------------------
# Schema field helpers
# ------------------------------------------------------------------
def field(name, cn, field_type, form_required, db_not_null, options=None):
    """Create a unified field definition used by both UI and database layers."""
    meta = {
        "form_required": form_required,
        "db_not_null": db_not_null,
    }
    if options is not None:
        meta["options"] = options
    return (name, cn, field_type, meta)


def unpack_field(field_def):
    """Normalize a field tuple into a stable dict shape."""
    name, cn, field_type, meta = field_def
    return {
        "name": name,
        "cn": cn,
        "type": field_type,
        "form_required": bool(meta.get("form_required", False)),
        "db_not_null": bool(meta.get("db_not_null", False)),
        "options": list(meta.get("options", [])),
    }


# Reusable field templates
_UPPER_BODY_FIELDS = [
    field("brand", "品牌", "text", True, True),
    field("model", "型号", "text", True, False),
    field("color", "配色", "text", True, False),
    field("article_no", "货号", "text", True, False),
    field("length_cm", "衣长", "decimal", True, False),
    field("chest_cm", "胸围", "decimal", True, False),
    field("shoulder_cm", "肩宽", "decimal", True, False),
    field("size_label", "尺码", "enum", True, False, ["XXS", "XS", "S", "M", "L", "XL", "2XL"]),
    field("purchase_date", "购买日期", "date", True, False),
    field("image_path", "图片", "image", True, False),
]

_LOWER_BODY_FIELDS = [
    field("brand", "品牌", "text", True, True),
    field("model", "型号", "text", True, False),
    field("color", "配色", "text", True, False),
    field("article_no", "货号", "text", True, False),
    field("length_cm", "裤长", "decimal", True, False),
    field("waist_cm", "腰围", "decimal", True, False),
    field("hip_cm", "臀围", "decimal", True, False),
    field("size_label", "尺码", "enum", True, False, ["XXS", "XS", "S", "M", "L", "XL", "2XL"]),
    field("purchase_date", "购买日期", "date", True, False),
    field("image_path", "图片", "image", True, False),
]

SCHEMA = {
    "short_sleeve": {
        "cn": "短袖",
        "icon": "👕",
        "fields": list(_UPPER_BODY_FIELDS),
    },
    "long_sleeve": {
        "cn": "长袖",
        "icon": "🧥",
        "fields": list(_UPPER_BODY_FIELDS),
    },
    "shorts": {
        "cn": "短裤",
        "icon": "🩳",
        "fields": list(_LOWER_BODY_FIELDS),
    },
    "trousers": {
        "cn": "长裤",
        "icon": "👖",
        "fields": list(_LOWER_BODY_FIELDS),
    },
    "socks": {
        "cn": "袜子",
        "icon": "🧦",
        "fields": [
            field("brand", "品牌", "text", True, True),
            field("model", "型号", "text", True, False),
            field("color", "配色", "text", True, False),
            field("article_no", "货号", "text", True, False),
            field("size_label", "尺码", "text", True, False),
            field("purchase_date", "购买日期", "date", True, False),
            field("image_path", "图片", "image", True, False),
        ],
    },
    "shoes": {
        "cn": "鞋子",
        "icon": "👟",
        "fields": [
            field("brand", "品牌", "text", True, True),
            field("model", "型号", "text", True, False),
            field("color", "配色", "text", True, False),
            field("article_no", "货号", "text", True, False),
            field("mm_size", "mm", "text", True, False),
            field("eur_size", "EUR", "text", True, False),
            field("purchase_date", "购买日期", "date", True, False),
            field("image_path", "图片", "image", True, False),
        ],
    },
    "car_models": {
        "cn": "汽车模型",
        "icon": "🚗",
        "fields": [
            field("scale", "比例", "text", True, False),
            field("real_brand", "实车品牌", "text", True, False),
            field("real_model", "实车型号", "text", True, False),
            field("color", "配色", "text", True, False),
            field("model_brand", "模型品牌", "text", True, False),
            field("purchase_date", "购买日期", "date", True, False),
            field("image_path", "图片", "image", True, False),
        ],
    },
    "driving_experience": {
        "cn": "驾驶经历",
        "icon": "🏎",
        "fields": [
            field("year", "年份", "text", True, False),
            field("model", "车型", "text", True, False),
            field("version", "版本", "text", True, False),
            field("drivetrain", "驱动形式", "text", True, False),
            field("image_path", "图片", "image", True, False),
        ],
    },
    "electronics": {
        "cn": "电子设备",
        "icon": "🔋",
        "fields": [
            field("category", "类别", "enum", True, True, ["手机", "平板", "手表", "耳机"]),
            field("brand", "品牌", "text", True, True),
            field("model", "型号", "text", True, False),
            field("color", "配色", "text", True, False),
            field("release_date", "发布日期", "date", True, False),
            field("purchase_date", "购买日期", "date", True, False),
            field("status", "状态", "enum", True, True, ["使用中", "闲置中", "已出售", "已损坏"]),
            field("image_path", "图片", "image", True, False),
        ],
    },
}

TABLE_ORDER = [
    "short_sleeve",
    "long_sleeve",
    "shorts",
    "trousers",
    "socks",
    "shoes",
    "car_models",
    "driving_experience",
    "electronics",
]

SORTABLE_COLS = {
    "short_sleeve": ["purchase_date"],
    "long_sleeve": ["purchase_date"],
    "shorts": ["purchase_date"],
    "trousers": ["purchase_date"],
    "socks": ["purchase_date"],
    "shoes": ["purchase_date"],
    "car_models": ["scale", "purchase_date"],
    "driving_experience": ["year"],
    "electronics": ["category", "purchase_date"],
}

COLORS = {
    # Backgrounds
    "bg": "#F5F5F7",
    "sidebar": "#F4F7FB",
    "sidebar_border": "#D7E0EA",
    "card": "#FFFFFF",
    "input_bg": "#FFFFFF",
    # Primary accent (blue)
    "accent": "#007AFF",
    "accent_hover": "#0051D5",
    "accent_light": "#DCEBFF",
    "accent_lighter": "#EEF5FF",
    "accent_selected_bg": "#ECF4FF",
    "accent_selected_border": "#CFE3FA",
    "accent_text": "#1658D1",
    "accent_selected_text": "#14529A",
    # Danger (red)
    "danger": "#FF3B30",
    "danger_hover": "#D63028",
    "danger_light": "#FFF1F0",
    "danger_text": "#C8332B",
    # Success (green)
    "success": "#34C759",
    "success_light": "#EAF7F0",
    "success_text": "#177245",
    # Text
    "text": "#1D1D1F",
    "text_secondary": "#86868B",
    # Borders & separators
    "separator": "#E5E5EA",
    "border": "#E2E9F0",
    "border_light": "#D5DDE8",
    "border_inner": "#E7EDF3",
    "border_row": "#EEF2F6",
    # Row states
    "row_hover": "#F2F2F7",
    "row_selected": "#EAF3FF",
    "row_even": "#F9FBFD",
    "input_border": "#D2D2D7",
}

IMAGE_FOLDERS = {
    "short_sleeve": {
        "_default": "short-sleeve pic",
    },
    "long_sleeve": {
        "_default": "long-sleeve pic",
    },
    "shorts": {
        "_default": "shorts pic",
    },
    "trousers": {
        "_default": "trousers pic",
    },
    "socks": {
        "_default": "socks pic",
    },
    "shoes": {
        "_default": "shoes pic",
    },
    "car_models": {
        "_default": "models pic",
    },
    "driving_experience": {
        "_default": "driving pic",
    },
    "electronics": {
        "_default": "electronics pic",
    },
}
