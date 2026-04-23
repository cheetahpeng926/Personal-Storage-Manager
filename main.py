#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Personal Storage Manager – Flet entry point."""

import logging
import os
import sys
import json
import threading

import flet as ft

from constants import COLORS, IMAGE_FOLDERS, LOG_PATH, PICTURES_DIR, SCHEMA, TABLE_ORDER, WINDOW_POSITION_FILE
from db import get_connection, init_database, ItemRepository
from services import ImageService
from ui import build_layout, refresh_sidebar_buttons, refresh_table, calc_visible_rows
from controllers import open_record_dialog, delete_record, pick_image, remove_image, pick_export_path, pick_import_path


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("psm")

CN_FONT = "PingFang SC"
EN_FONT = "SF Pro Text"


def _parse_semver(ver: str):
    core = (ver or "").split("-", 1)[0].split("+", 1)[0]
    parts = core.split(".")
    nums = []
    for p in parts[:3]:
        try:
            nums.append(int(p))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


class PersonalStorageApp:
    """Thin application state holder; UI and logic live in ui.py / controllers.py."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.cn_font = CN_FONT
        self.en_font = EN_FONT
        self.conn = get_connection()
        self.repo = ItemRepository(self.conn)
        self.image_service = ImageService(PICTURES_DIR, IMAGE_FOLDERS)
        self.image_service.ensure_picture_dirs()

        self.current_table = TABLE_ORDER[0]
        self.current_row_id = None
        self.selected_row_ids = set()  # Multi-selection support
        self.multi_select_mode = False  # Toggle via button
        self.current_image_path = None
        self.sort_col = None
        self.sort_dir = 0
        self._initialized = False
        self._last_visible_rows = -1
        self._search_timer = None
        self._search_lock = threading.Lock()

        self.sidebar_buttons = {}

        self.search_field = ft.TextField(
            hint_text="搜索",
            text_size=14,
            dense=True,
            border_radius=10,
            border_color=COLORS["border_light"],
            bgcolor=COLORS["input_bg"],
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            on_change=self._on_search_change,
            hint_style=ft.TextStyle(color=COLORS["text_secondary"]),
        )

        self.count_text = ft.Text("共 0 条记录", size=12, weight=ft.FontWeight.W_600, color=COLORS["text_secondary"])
        self.title_text = ft.Text(size=24, weight=ft.FontWeight.W_600, color=COLORS["text"])
        self.title_icon = ft.Text(size=24, weight=ft.FontWeight.W_600)

        self.table_header_row = ft.Row(spacing=0)
        self.table_list = ft.ListView(spacing=0, auto_scroll=False, expand=True)

        self.preview_inner = ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=ft.Text("选中记录后\n显示图片", weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER, color=COLORS["text_secondary"]),
        )
        self.file_picker = ft.FilePicker()

    # ------------------------------------------------------------------
    # Page setup & window state
    # ------------------------------------------------------------------

    def setup_page(self):
        self.page.title = "Personal Storage Manager"
        self.page.padding = 0
        self.page.spacing = 0
        self.page.bgcolor = COLORS["bg"]

        # Register bundled fonts (works in dev & packaged exe)
        cn_font_path = os.path.join(os.path.dirname(LOG_PATH), "PingFangSC-Regular.ttf")
        en_font_path = os.path.join(os.path.dirname(LOG_PATH), "SF-Pro-Text-Regular.otf")
        fonts = {}
        if os.path.isfile(cn_font_path):
            fonts[self.cn_font] = cn_font_path
        if os.path.isfile(en_font_path):
            fonts[self.en_font] = en_font_path
        if fonts:
            self.page.fonts = fonts

        self.page.theme = ft.Theme(font_family=self.cn_font)
        self.page.dark_theme = ft.Theme(font_family=self.cn_font)
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self._apply_window_state()
        self.page.window.min_width = 1060
        self.page.window.min_height = 600

        icon_path = os.path.join(os.path.dirname(LOG_PATH), "icon.ico")
        if os.path.isfile(icon_path):
            try:
                self.page.window.icon = icon_path
            except Exception:
                logger.debug("当前 Flet 客户端不支持设置窗口图标")

        self.page.services.append(self.file_picker)
        self.page.on_resize = self.on_page_resize
        self.page.window.on_event = self.on_window_event

    def _load_window_state(self):
        if not os.path.isfile(WINDOW_POSITION_FILE):
            return {}
        try:
            with open(WINDOW_POSITION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
        except Exception:
            logger.exception("读取窗口状态失败")
        return {}

    def _save_window_state(self):
        try:
            left = self.page.window.left
            top = self.page.window.top
            width = self.page.window.width
            height = self.page.window.height
        except Exception:
            return

        payload = {}
        if isinstance(left, (int, float)):
            payload["left"] = int(left)
        if isinstance(top, (int, float)):
            payload["top"] = int(top)
        if isinstance(width, (int, float)):
            payload["width"] = int(width)
        if isinstance(height, (int, float)):
            payload["height"] = int(height)

        if len(payload) < 2:
            return

        try:
            with open(WINDOW_POSITION_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception:
            logger.exception("保存窗口状态失败")

    def _apply_window_state(self):
        state = self._load_window_state()
        self.page.window.width = int(state.get("width", 1235))
        self.page.window.height = int(state.get("height", 763))

        left = state.get("left", state.get("x"))
        top = state.get("top", state.get("y"))
        if isinstance(left, (int, float)):
            self.page.window.left = int(left)
        if isinstance(top, (int, float)):
            self.page.window.top = int(top)

    # ------------------------------------------------------------------
    # Event handlers (merged resize logic with debounce)
    # ------------------------------------------------------------------

    def _handle_resize(self):
        """Unified resize handler — debounced to avoid double-trigger."""
        if not self._initialized:
            return
        self._save_window_state()
        new_visible = calc_visible_rows(self.page)
        if new_visible != self._last_visible_rows:
            self._last_visible_rows = new_visible
            self.refresh_table()

    def _on_search_change(self, e):
        """Debounced search handler (300ms delay)."""
        with self._search_lock:
            if self._search_timer:
                self._search_timer.cancel()
            self._search_timer = threading.Timer(0.3, self._do_search)
            self._search_timer.start()

    def _do_search(self):
        """Execute the actual search after debounce."""
        try:
            self.refresh_table()
        except Exception:
            pass

    def on_page_resize(self, e):
        if not self._initialized:
            self._initialized = True
            return
        self._handle_resize()

    def on_window_event(self, e):
        event_type = getattr(e, "type", None)
        event_name = str(event_type.value).lower() if event_type else ""
        if event_name in ("resize", "resized", "restore", "maximize", "unmaximize"):
            self._handle_resize()
        else:
            self._save_window_state()

    # ------------------------------------------------------------------
    # Delegated methods (forward to modules)
    # ------------------------------------------------------------------

    def run(self):
        self.setup_page()
        build_layout(self)
        self.refresh_title()
        self.refresh_sidebar_buttons()
        self.refresh_table()
        self.page.update()
        self._initialized = True

    def refresh_title(self):
        schema = SCHEMA[self.current_table]
        self.title_icon.value = schema["icon"]
        self.title_text.value = schema["cn"]

    def switch_table(self, table):
        self.current_table = table
        self.current_row_id = None
        self.selected_row_ids = set()
        self.sort_col = None
        self.sort_dir = 0
        self.search_field.value = ""
        self.refresh_title()
        self.refresh_preview(None)
        self.refresh_sidebar_buttons()
        self.refresh_table()

    def toggle_multi_select(self, active):
        """Toggle multi-select mode from button."""
        self.multi_select_mode = active
        # Update button appearance
        if active:
            self.multi_select_btn.bgcolor = COLORS["accent_light"]
            self.multi_select_btn.border = ft.Border.all(1, COLORS["accent"])
            self.multi_select_btn.content = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Text("☑", size=14, color=COLORS["accent_text"]),
                    ft.Text("多选", size=14, weight=ft.FontWeight.W_600, color=COLORS["accent_text"]),
                ],
            )
        else:
            self.multi_select_btn.bgcolor = COLORS["card"]
            self.multi_select_btn.border = ft.Border.all(1, COLORS["border"])
            self.multi_select_btn.content = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Text("☑", size=14),
                    ft.Text("多选", size=14, weight=ft.FontWeight.W_600, color=COLORS["text"]),
                ],
            )
        if not active:
            # Keep only current row selected
            if self.current_row_id and self.current_row_id in self.selected_row_ids:
                self.selected_row_ids = {self.current_row_id}
            else:
                self.selected_row_ids = set()
        self.refresh_table()

    def select_row(self, rid):
        """Handle row click - respects multi-select mode."""
        if self.multi_select_mode:
            # Toggle selection
            if rid in self.selected_row_ids:
                self.selected_row_ids.discard(rid)
                if self.current_row_id == rid:
                    self.current_row_id = next(iter(self.selected_row_ids), None)
            else:
                self.selected_row_ids.add(rid)
                self.current_row_id = rid
        else:
            # Single select
            self.selected_row_ids = {rid}
            self.current_row_id = rid
        self.refresh_table()
        if self.current_row_id:
            self.refresh_preview(self.repo.get_image_path(self.current_table, self.current_row_id))

    def toggle_sort(self, col):
        if self.sort_col == col:
            self.sort_dir = {1: 2, 2: 0}.get(self.sort_dir, 1)
            if self.sort_dir == 0:
                self.sort_col = None
        else:
            self.sort_col = col
            self.sort_dir = 1
        self.refresh_table()

    def refresh_preview(self, img_path):
        self.current_image_path = img_path if img_path and os.path.isfile(img_path) else None
        if self.current_image_path:
            self.preview_inner.content = ft.Image(
                src=self.current_image_path,
                fit=ft.BoxFit.CONTAIN,
                border_radius=10,
            )
        else:
            self.preview_inner.content = ft.Text("选中记录后\n显示图片", weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER, color=COLORS["text_secondary"])
        self.page.update()

    def add_record(self):
        open_record_dialog(self)

    def edit_record(self):
        if len(self.selected_row_ids) > 1:
            self.show_snack("编辑仅支持单选，请只选择一条记录")
            return
        if self.current_row_id is None:
            self.show_snack("请先选择一条记录")
            return
        row = self.repo.get_record_by_id(self.current_table, self.current_row_id)
        if not row:
            self.show_snack("记录不存在")
            return
        open_record_dialog(self, initial=dict(row))

    def delete_record(self):
        delete_record(self, list(self.selected_row_ids))

    async def pick_image(self):
        await pick_image(self)

    def remove_image(self):
        remove_image(self)

    async def pick_import_path(self):
        await pick_import_path(self)

    async def pick_export_path(self):
        await pick_export_path(self)

    def refresh_sidebar_buttons(self):
        refresh_sidebar_buttons(self)

    def refresh_table(self):
        refresh_table(self)

    def show_snack(self, text):
        self.page.snack_bar = ft.SnackBar(ft.Text(text, weight=ft.FontWeight.W_600), open=True)
        self.page.update()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            logger.exception("关闭数据库连接失败")


def main(page: ft.Page):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    flet_ver = getattr(ft, "__version__", "0.0.0")
    if _parse_semver(flet_ver) < (0, 84, 0):
        raise RuntimeError(f"当前 Flet 版本过低: {flet_ver}，请升级到 0.84.0")
    init_database()
    app = PersonalStorageApp(page)

    def on_disconnect(e):
        app._save_window_state()
        app.close()

    page.on_disconnect = on_disconnect
    app.run()


if __name__ == "__main__":
    ft.run(main, assets_dir=PICTURES_DIR)
