# -*- coding: utf-8 -*-
"""Flet UI layout and rendering for Personal Storage Manager."""

import inspect
import os

import flet as ft

from constants import COLORS, SCHEMA, TABLE_ORDER, SORTABLE_COLS, unpack_field


ROW_HEIGHT = 40


def _build_cell(value, field_name):
    """Build a single table cell container."""
    text = "—" if value is None else str(value)
    return ft.Container(
        expand=get_column_expand(field_name),
        height=ROW_HEIGHT,
        alignment=ft.Alignment(0, 0),
        padding=ft.Padding.symmetric(horizontal=8, vertical=8),
        content=ft.Text(
            text,
            size=13,
            weight=ft.FontWeight.W_600,
            color=COLORS["text"],
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            text_align=ft.TextAlign.CENTER,
        ),
    )


# ------------------------------------------------------------------
# Widget builders (merged from widgets.py)
# ------------------------------------------------------------------
def build_action_button(page, text, icon, bg, color, on_click, full_width=False, custom_width=None):
    """Build a styled action button container."""
    button_width = custom_width if custom_width is not None else (205 if full_width else None)

    def handle_click(e):
        if inspect.iscoroutinefunction(on_click):
            page.run_task(on_click)
            return
        result = on_click()
        if inspect.isawaitable(result):
            async def await_result():
                await result
            page.run_task(await_result)

    return ft.Container(
        width=button_width,
        height=36,
        border_radius=12,
        bgcolor=bg,
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        ink=True,
        on_click=handle_click,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER if full_width else ft.MainAxisAlignment.START,
            spacing=8,
            controls=[
                ft.Text(icon, size=15, weight=ft.FontWeight.W_600),
                ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=color),
            ],
        ),
    )


# ------------------------------------------------------------------
# Field helpers
# ------------------------------------------------------------------


def get_display_fields(table):
    fields = []
    for field_def in SCHEMA[table]["fields"]:
        field = unpack_field(field_def)
        if field["name"] not in ("id", "image_path"):
            fields.append(field)
    return fields


def get_text_fields(table):
    return [field["name"] for field in get_display_fields(table) if field["type"] == "text"]


def get_column_expand(field_name):
    if field_name.endswith("_at") or "date" in field_name:
        return 2
    return 1


def build_layout(app):
    """Build the full page layout. Returns nothing; adds to page directly."""
    page = app.page
    cn_font = app.cn_font
    en_font = app.en_font

    sidebar = ft.Container(
        width=235,
        bgcolor=COLORS["sidebar"],
        border=ft.Border.only(right=ft.BorderSide(1, COLORS["sidebar_border"])),
        padding=ft.Padding.only(left=12, top=14, right=12, bottom=14),
        content=ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=ft.Padding.only(bottom=6),
                    content=ft.Column(
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("📦", size=35, weight=ft.FontWeight.W_600),
                            ft.Text("Personal Storage", size=17, weight=ft.FontWeight.W_600, font_family=en_font, color=COLORS["text"]),
                            ft.Text("Manager", size=17, weight=ft.FontWeight.W_600, font_family=en_font, color=COLORS["text"]),
                            ft.Text("Made by PWR", size=10, weight=ft.FontWeight.W_500, font_family=en_font, color=COLORS["text_secondary"]),
                            ft.Text("Built by Xiaomi MiMo & GPT & Z.AI GLM", size=10, weight=ft.FontWeight.W_500, font_family=en_font, color=COLORS["text_secondary"]),
                        ],
                    ),
                ),
                ft.Divider(height=1, thickness=1, color=COLORS["sidebar_border"]),
                ft.Text("分 类", size=12, weight=ft.FontWeight.W_500, color=COLORS["text_secondary"]),
                ft.Column(spacing=8, controls=[_build_sidebar_button(app, t) for t in TABLE_ORDER]),
                ft.Container(expand=True),
                build_action_button(page, "导 入", "📥", COLORS["accent_lighter"], COLORS["accent_text"], app.pick_import_path, full_width=True),
                build_action_button(page, "导 出", "📤", COLORS["success_light"], COLORS["success_text"], app.pick_export_path, full_width=True),
            ],
        ),
    )

    # Multi-select toggle button
    app.multi_select_btn = ft.Container(
        width=80,
        height=36,
        border_radius=12,
        bgcolor=COLORS["card"],
        border=ft.Border.all(1, COLORS["border"]),
        ink=True,
        on_click=lambda e: app.toggle_multi_select(not app.multi_select_mode),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Text("☑", size=14),
                ft.Text("多选", size=14, weight=ft.FontWeight.W_600, color=COLORS["text"]),
            ],
        ),
    )

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=2,
                controls=[
                    ft.Row(spacing=8, controls=[app.title_icon, app.title_text]),
                    app.count_text,
                ],
            ),
            ft.Row(
                spacing=8,
                controls=[
                    ft.Container(width=220, content=app.search_field),
                    app.multi_select_btn,
                    ft.Container(width=260, content=ft.Row(
                        spacing=8,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            build_action_button(page, "新增", "＋", COLORS["accent_light"], COLORS["accent_text"], app.add_record),
                            build_action_button(page, "编辑", "✎", COLORS["accent_lighter"], COLORS["accent_text"], app.edit_record),
                            build_action_button(page, "删除", "🗑", COLORS["danger_light"], COLORS["danger_text"], app.delete_record),
                        ],
                    )),
                ],
            ),
        ],
    )

    table_card = ft.Container(
        expand=True,
        bgcolor=COLORS["card"],
        border_radius=14,
        border=ft.Border.all(1, COLORS["border"]),
        padding=12,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                app.table_header_row,
                ft.Container(
                    expand=True,
                    content=app.table_list,
                ),
            ],
        ),
    )

    preview_card = ft.Container(
        width=260,
        bgcolor=COLORS["card"],
        border_radius=14,
        border=ft.Border.all(1, COLORS["border"]),
        padding=12,
        content=ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Text("图片预览", size=15, weight=ft.FontWeight.W_600, color=COLORS["text"]),
                ft.Container(
                    expand=True,
                    border_radius=12,
                    bgcolor=COLORS["row_even"],
                    border=ft.Border.all(1, COLORS["border_inner"]),
                    padding=8,
                    content=app.preview_inner,
                ),
                build_action_button(page, "更换图片", "🖼", COLORS["accent_light"], COLORS["accent_text"], app.pick_image, full_width=True, custom_width=236),
                build_action_button(page, "删除图片", "✕", COLORS["danger_light"], COLORS["danger_text"], app.remove_image, full_width=True, custom_width=236),
            ],
        ),
    )

    body = ft.Row(expand=True, spacing=12, controls=[table_card, preview_card])

    content = ft.Container(
        expand=True,
        padding=ft.Padding.only(left=20, top=18, right=20, bottom=18),
        content=ft.Column(expand=True, spacing=12, controls=[header, body]),
    )

    page.add(ft.Row(expand=True, spacing=0, controls=[sidebar, content]))


def _build_sidebar_button(app, table):
    """Create a single sidebar button container."""
    button = ft.Container(on_click=lambda e, t=table: app.switch_table(t))
    app.sidebar_buttons[table] = button
    return button


def refresh_sidebar_buttons(app):
    """Update all sidebar button appearances based on current selection."""
    for table, button in app.sidebar_buttons.items():
        schema = SCHEMA[table]
        selected = table == app.current_table

        if selected:
            button.content = ft.Container(
                border_radius=14,
                height=38,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                bgcolor=COLORS["accent_selected_bg"],
                border=ft.Border.all(1, COLORS["accent_selected_border"]),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Text(schema["icon"], size=18, weight=ft.FontWeight.W_600),
                        ft.Text(schema["cn"], size=15, weight=ft.FontWeight.W_600, color=COLORS["accent_selected_text"]),
                    ],
                ),
            )
        else:
            button.content = ft.Container(
                border_radius=14,
                height=38,
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        ft.Text(schema["icon"], size=18, weight=ft.FontWeight.W_600),
                        ft.Text(schema["cn"], size=15, weight=ft.FontWeight.W_600, color=COLORS["text"]),
                    ],
                ),
            )
    app.page.update()


# Layout constants for estimating visible rows
_OUTER_PAD_TOP = 18
_OUTER_PAD_BOTTOM = 18
_HEADER_HEIGHT = 36
_BODY_SPACING = 12
_TABLE_CARD_PAD = 12
_TABLE_HEADER_H = 34


def calc_visible_rows(page):
    """Estimate how many rows can fit in the current table area."""
    try:
        page_h = page.height or 763
    except Exception:
        page_h = 763
    available = (page_h
                 - _OUTER_PAD_TOP
                 - _OUTER_PAD_BOTTOM
                 - _HEADER_HEIGHT
                 - _BODY_SPACING
                 - _TABLE_CARD_PAD * 2
                 - _TABLE_HEADER_H)
    available = max(available, 0)
    return max(1, int(available // ROW_HEIGHT))


def _build_empty_row(display_fields):
    cells = [_build_cell("", f["name"]) for f in display_fields]
    return ft.Container(
        border=ft.Border.only(bottom=ft.BorderSide(1, COLORS["border_row"])),
        content=ft.Row(spacing=0, controls=cells),
    )


def _build_data_row(app, display_fields, row, selected=False):
    cells = [_build_cell(row[f["name"]], f["name"]) for f in display_fields]
    rid = row["id"]
    return ft.Container(
        bgcolor=COLORS["row_selected"] if selected else COLORS["card"],
        border=ft.Border.only(bottom=ft.BorderSide(1, COLORS["border_row"])),
        ink=True,
        on_click=lambda e: app.select_row(rid),
        content=ft.Row(spacing=0, controls=cells),
    )


def refresh_table(app):
    """Rebuild the table header and data rows."""
    table = app.current_table
    display_fields = get_display_fields(table)
    rows = app.repo.list_records(
        table,
        search_text=(app.search_field.value or "").strip(),
        text_fields=get_text_fields(table),
        sort_col=app.sort_col,
        sort_dir=app.sort_dir,
    )

    sortable = SORTABLE_COLS.get(table, [])
    headers = []
    for field in display_fields:
        label = field["cn"]
        if field["name"] in sortable:
            if app.sort_col == field["name"] and app.sort_dir == 1:
                label += " ▲"
            elif app.sort_col == field["name"] and app.sort_dir == 2:
                label += " ▼"
            else:
                label += " ↕"

        headers.append(
            ft.Container(
                expand=get_column_expand(field["name"]),
                height=34,
                alignment=ft.Alignment(0, 0),
                border=ft.Border.only(bottom=ft.BorderSide(1, COLORS["border_inner"])),
                padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                on_click=(lambda e, c=field["name"]: app.toggle_sort(c)) if field["name"] in sortable else None,
                content=ft.Text(
                    label,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=COLORS["text"],
                    text_align=ft.TextAlign.CENTER,
                ),
            )
        )

    app.table_header_row.controls = headers

    controls = []
    for row in rows:
        is_selected = row["id"] in app.selected_row_ids
        controls.append(_build_data_row(app, display_fields, row, selected=is_selected))

    # Pad with empty placeholder rows to fill the table area
    visible_rows = calc_visible_rows(app.page)
    app._last_visible_rows = visible_rows
    if len(controls) < visible_rows:
        # If no data at all, show friendly empty state message
        if len(rows) == 0:
            empty_height = visible_rows * ROW_HEIGHT
            empty_msg = ft.Container(
                height=empty_height,
                alignment=ft.Alignment(0.5, 0.5),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Text("📭", size=40),
                                ft.Text("暂无记录", size=16, weight=ft.FontWeight.W_600, color=COLORS["text_secondary"]),
                                ft.Text("点击右上角「新增」按钮添加", size=13, color=COLORS["text_secondary"]),
                            ],
                        )
                    ],
                ),
            )
            app.table_list.controls = [empty_msg]
            app.count_text.value = "共 0 条记录"
            app.page.update()
            return
        for _ in range(visible_rows - len(controls)):
            controls.append(_build_empty_row(display_fields))

    app.table_list.controls = controls
    app.count_text.value = f"共 {len(rows)} 条记录"
    app.page.update()
