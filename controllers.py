# -*- coding: utf-8 -*-
"""Flet controllers for record actions, dialogs, and export flows."""

import logging
import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

import flet as ft

from constants import COLORS, LOG_PATH, PICTURES_DIR, SCHEMA, TABLE_ORDER, unpack_field, resolve_image_path
from services import export_to_zip, import_from_zip
from ui import get_display_fields

logger = logging.getLogger("psm.controllers")


def open_record_dialog(app, initial=None):
    """Open add/edit record dialog."""
    initial = initial or {}
    fields = [field for field in get_display_fields(app.current_table) if field["name"] != "created_at"]
    inputs = {}
    controls = []

    for field in fields:
        value = initial.get(field["name"])
        if field["type"] == "enum":
            control = ft.Dropdown(
                label=field["cn"],
                value=str(value) if value is not None else (field["options"][0] if field["options"] else None),
                options=[ft.dropdown.Option(opt) for opt in field["options"]],
                border_radius=12,
                width=420,
            )
        else:
            control = ft.TextField(
                label=field["cn"],
                value="" if value is None else str(value),
                border_radius=12,
                text_align=ft.TextAlign.CENTER,
                width=420,
            )
        inputs[field["name"]] = (field, control)
        controls.append(control)

    error_text = ft.Text("", color=COLORS["danger"], size=14, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.LEFT)
    
    def show_error(msg):
        error_text.value = msg
        dialog.update()
    
    def on_submit(e):
        error_text.value = ""  # Clear previous error
        payload = {}
        for name, (field, control) in inputs.items():
            value = (control.value or "").strip()
            if field["form_required"] and not value:
                show_error(f"{field['cn']} 为必填项")
                return
            if not value:
                payload[name] = None
                continue
            if field["type"] == "decimal":
                try:
                    payload[name] = Decimal(value)
                except InvalidOperation:
                    show_error(f"{field['cn']} 请输入有效数字")
                    return
            elif field["type"] == "date":
                # Support multiple formats, normalize to YYYY.MM.DD
                normalized = None
                # 8-digit: YYYYMMDD
                if re.match(r"^\d{8}$", value):
                    normalized = f"{value[:4]}.{value[4:6]}.{value[6:8]}"
                # YYYY-MM-DD
                elif re.match(r"^\d{4}-\d{1,2}-\d{1,2}$", value):
                    parts = value.split("-")
                    normalized = f"{parts[0]}.{int(parts[1]):02d}.{int(parts[2]):02d}"
                # YYYY.MM.DD
                elif re.match(r"^\d{4}\.\d{1,2}\.\d{1,2}$", value):
                    parts = value.split(".")
                    normalized = f"{parts[0]}.{int(parts[1]):02d}.{int(parts[2]):02d}"
                # YYYY/MM/DD
                elif re.match(r"^\d{4}/\d{1,2}/\d{1,2}$", value):
                    parts = value.split("/")
                    normalized = f"{parts[0]}.{int(parts[1]):02d}.{int(parts[2]):02d}"
                else:
                    # Format not matched
                    show_error(f"{field['cn']} 格式错误，可输入：YYYYMMDD")
                    return
                
                try:
                    datetime.strptime(normalized, "%Y.%m.%d")
                except ValueError:
                    show_error(f"{field['cn']} 无效")
                    return
                payload[name] = normalized
            else:
                payload[name] = value.replace("：", ":") if name == "scale" else value

        try:
            if initial:
                app.repo.update_record(app.current_table, app.current_row_id, payload)
            else:
                new_id = app.repo.insert_record(app.current_table, payload)
                app.current_row_id = new_id
        except Exception as e:
            logger.exception("保存记录失败")
            show_error(f"保存失败: {e}")
            return

        app.page.pop_dialog()
        app.refresh_table()
        if app.current_row_id:
            app.refresh_preview(app.repo.get_image_path(app.current_table, app.current_row_id))

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(("编辑" if initial else "新增") + SCHEMA[app.current_table]["cn"], weight=ft.FontWeight.W_600),
        content=ft.Container(
            width=420,
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=controls + [error_text],
                tight=True,
            ),
        ),
        actions=[
            ft.TextButton("取消", on_click=lambda e: app.page.pop_dialog()),
            ft.FilledButton("确定", on_click=on_submit),
        ],
    )
    app.page.show_dialog(dialog)


def delete_record(app, row_ids):
    """Delete one or more selected records."""
    if not row_ids:
        app.show_snack("请先选择记录")
        return

    count = len(row_ids)
    table_cn = SCHEMA[app.current_table]["cn"]

    def confirm_delete(e):
        success_count = 0
        for rid in row_ids:
            try:
                old_path = app.repo.get_image_path(app.current_table, rid)
                app.repo.delete_record(app.current_table, rid)
                app.image_service.remove_image_file(old_path)
                success_count += 1
            except Exception:
                logger.exception(f"删除记录 {rid} 失败")
        app.current_row_id = None
        app.selected_row_ids = set()
        app.page.pop_dialog()
        app.refresh_preview(None)
        app.refresh_table()
        if success_count < count:
            app.show_snack(f"已删除 {success_count}/{count} 条记录")
        else:
            app.show_snack(f"已删除 {success_count} 条记录")

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("确认删除", weight=ft.FontWeight.W_600),
        content=ft.Text(f"确定删除选中的 {count} 条{table_cn}记录？此操作不可撤销。", weight=ft.FontWeight.W_600),
        actions=[
            ft.TextButton("取消", on_click=lambda e: app.page.pop_dialog()),
            ft.FilledButton("删除", bgcolor=COLORS["danger_hover"], on_click=confirm_delete),
        ],
    )
    app.page.show_dialog(dialog)


async def pick_image(app):
    """Open file picker to change image for selected record."""
    if app.current_row_id is None:
        app.show_snack("请先选择一条记录")
        return
    files = await app.file_picker.pick_files(
        dialog_title="选择图片",
        file_type=ft.FilePickerFileType.IMAGE,
        allow_multiple=False,
    )
    if not files:
        return

    src = files[0].path
    if not src or not os.path.isfile(src):
        app.show_snack("图片路径不存在")
        return

    row = app.repo.get_record_by_id(app.current_table, app.current_row_id)
    if not row:
        app.show_snack("记录不存在")
        return

    try:
        dst = app.image_service.replace_image(app.current_table, dict(row), src)
        app.repo.update_image_path(app.current_table, app.current_row_id, dst)
    except Exception:
        logger.exception("更换图片失败")
        app.show_snack("更换图片失败，请重试")
        return
    # dst is relative path; resolve for preview display
    app.refresh_preview(resolve_image_path(dst))
    app.refresh_table()


def remove_image(app):
    """Remove image from the currently selected record."""
    if app.current_row_id is None:
        app.show_snack("请先选择一条记录")
        return
    # get_image_path already resolves relative paths via resolve_image_path
    try:
        old_path = app.repo.get_image_path(app.current_table, app.current_row_id)
        app.repo.update_image_path(app.current_table, app.current_row_id, None)
        app.image_service.remove_image_file(old_path)
    except Exception:
        logger.exception("删除图片失败")
        app.show_snack("删除图片失败，请重试")
        return
    app.refresh_preview(None)
    app.refresh_table()


async def pick_import_path(app):
    """Open file picker to import data and images from ZIP."""
    files = await app.file_picker.pick_files(
        dialog_title="导入数据",
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["zip"],
    )
    if not files:
        return
    src_path = files[0].path
    if not src_path or not os.path.isfile(src_path):
        app.show_snack("文件不存在")
        return
    result = import_from_zip(
        src_path,
        TABLE_ORDER,
        SCHEMA,
        lambda table, data: app.repo.insert_record(table, data),
        list_fn=lambda table: app.repo.list_records(table),
        pictures_dir=PICTURES_DIR,
        update_fn=lambda table, rid, data: app.repo.update_record(table, rid, data),
    )
    if result.get("error") == "missing_openpyxl":
        app.show_snack("缺少 openpyxl，无法导入")
        return
    if result.get("error") == "invalid_file":
        msg = result.get("message", "文件格式无效")
        app.show_snack(f"导入失败：{msg}")
        return
    total = result["total_records"]
    skipped = result.get("skipped", 0)
    images = result.get("image_count", 0)
    errors = result.get("errors", [])
    msg = f"导入完成：新增 {total} 条"
    if images:
        msg += f"，图片 {images} 张"
    if skipped:
        msg += f"，跳过重复 {skipped} 条"
    if errors:
        msg += f"，失败 {len(errors)} 条"
    app.show_snack(msg)
    app.refresh_table()


async def pick_export_path(app):
    """Open file picker to export all data and images to ZIP."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_path = os.path.join(os.path.dirname(LOG_PATH), f"Storage_Backup_{ts}.zip")
    save_path = await app.file_picker.save_file(
        dialog_title="导出全部数据",
        file_name=os.path.basename(default_path),
        initial_directory=os.path.dirname(default_path),
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["zip"],
    )
    if not save_path:
        return

    if not save_path.lower().endswith(".zip"):
        save_path += ".zip"

    folder = os.path.dirname(save_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    result = export_to_zip(
        save_path,
        TABLE_ORDER,
        SCHEMA,
        lambda table: app.repo.list_records(table),
        pictures_dir=PICTURES_DIR,
    )
    if result.get("error") == "missing_openpyxl":
        app.show_snack("缺少 openpyxl，无法导出")
        return
    if result["total_records"] == 0:
        app.show_snack("所有分类都没有数据可导出")
        return
    images = result.get("image_count", 0)
    msg = f"导出成功：{result['total_records']} 条记录"
    if images:
        msg += f"，{images} 张图片"
    app.show_snack(msg)
