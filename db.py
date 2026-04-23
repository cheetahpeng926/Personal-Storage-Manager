# -*- coding: utf-8 -*-
"""数据库建表与连接 (SQLite 版)"""

import logging
import re
import sqlite3
from decimal import Decimal

from constants import DB_PATH, PICTURES_DIR, SCHEMA, unpack_field, resolve_image_path


logger = logging.getLogger("psm.db")
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def get_connection():
    """获取 SQLite 数据库连接，返回 Row 模式（支持 dict 风格访问）"""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _validate_identifier(name):
    if not _IDENTIFIER_RE.fullmatch(name):
        raise ValueError(f"Invalid SQL identifier: {name}")
    return name


def _sqlite_type(field_type):
    if field_type == "decimal":
        return "REAL"
    return "TEXT"


def _create_table_sql(table, table_schema):
    table = _validate_identifier(table)
    columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]

    for field_def in table_schema["fields"]:
        field = unpack_field(field_def)
        field_name = _validate_identifier(field["name"])
        sqlite_type = _sqlite_type(field["type"])
        constraints = " NOT NULL" if field["db_not_null"] else ""

        if table == "electronics" and field_name == "status":
            constraints += " DEFAULT '使用中'"

        columns.append(f"{field_name} {sqlite_type}{constraints}")

    columns.append("created_at TEXT DEFAULT (datetime('now', 'localtime'))")
    joined = ",\n        ".join(columns)
    return f"CREATE TABLE IF NOT EXISTS {table} (\n        {joined}\n    )"


class ItemRepository:
    def __init__(self, connection=None):
        self._conn = connection or get_connection()

    def close(self):
        self._conn.close()

    def get_record_by_id(self, table, rid):
        table = _validate_identifier(table)
        cur = self._conn.cursor()
        cur.execute(f"SELECT * FROM `{table}` WHERE id = ?", (rid,))
        row = cur.fetchone()
        cur.close()
        return row

    def get_image_path(self, table, rid):
        row = self.get_record_by_id(table, rid)
        if not row:
            return None
        return resolve_image_path(row["image_path"])

    def list_records(self, table, *, search_text="", text_fields=None, sort_col=None, sort_dir=0):
        table = _validate_identifier(table)
        text_fields = text_fields or []

        order_by = "`id` DESC"
        if sort_col and sort_dir in (1, 2):
            sort_col = _validate_identifier(sort_col)
            direction = "ASC" if sort_dir == 1 else "DESC"
            order_by = f"`{sort_col}` {direction}, `id` DESC"

        cur = self._conn.cursor()
        search_text = (search_text or "").strip()
        valid_fields = [_validate_identifier(field) for field in text_fields]
        if search_text and valid_fields:
            conditions = " OR ".join(f"`{field}` LIKE ?" for field in valid_fields)
            params = [f"%{search_text}%"] * len(valid_fields)
            cur.execute(f"SELECT * FROM `{table}` WHERE {conditions} ORDER BY {order_by}", params)
        else:
            cur.execute(f"SELECT * FROM `{table}` ORDER BY {order_by}")

        rows = cur.fetchall()
        cur.close()
        return rows

    def insert_record(self, table, data):
        table = _validate_identifier(table)
        fields = [_validate_identifier(field) for field, value in data.items() if value is not None]
        if not fields:
            return None

        placeholders = ", ".join(f"`{field}`" for field in fields)
        # Convert Decimal to string for SQLite compatibility
        values = []
        for field in fields:
            val = data[field]
            if isinstance(val, Decimal):
                val = str(val)
            values.append(val)
        marks = ", ".join("?" for _ in fields)

        cur = self._conn.cursor()
        cur.execute(f"INSERT INTO `{table}` ({placeholders}) VALUES ({marks})", values)
        self._conn.commit()
        new_id = cur.lastrowid
        cur.close()
        return new_id

    def update_record(self, table, rid, data):
        table = _validate_identifier(table)
        fields = [_validate_identifier(field) for field in data]
        if not fields:
            return

        sets = ", ".join(f"`{field}` = ?" for field in fields)
        # Convert Decimal to string for SQLite compatibility
        values = []
        for field in fields:
            val = data[field]
            if isinstance(val, Decimal):
                val = str(val)
            values.append(val)
        values.append(rid)

        cur = self._conn.cursor()
        cur.execute(f"UPDATE `{table}` SET {sets} WHERE id = ?", values)
        self._conn.commit()
        cur.close()

    def update_image_path(self, table, rid, image_path):
        self.update_record(table, rid, {"image_path": image_path})

    def delete_record(self, table, rid):
        table = _validate_identifier(table)
        cur = self._conn.cursor()
        cur.execute(f"DELETE FROM `{table}` WHERE id = ?", (rid,))
        self._conn.commit()
        cur.close()


def init_database():
    """按当前 SCHEMA 初始化缺失的数据表，不处理旧表迁移。"""
    conn = get_connection()
    cur = conn.cursor()

    for table, table_schema in SCHEMA.items():
        cur.execute(_create_table_sql(table, table_schema))

    conn.commit()
    cur.close()
    conn.close()
    logger.info("数据库初始化完成: %s", DB_PATH)


if __name__ == "__main__":
    init_database()
