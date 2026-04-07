# -*- coding: utf-8 -*-
"""数据库建表与连接 (SQLite 版)"""

import sqlite3
from config import DB_PATH


def get_connection():
    """获取 SQLite 数据库连接，返回 Row 模式（支持 dict 风格访问）"""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database():
    """建表，幂等操作"""
    conn = get_connection()
    cur = conn.cursor()

    # ── 短袖 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS short_sleeve (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        brand           TEXT NOT NULL                /* 品牌 */,
        model           TEXT                         /* 型号 */,
        color           TEXT                         /* 配色 */,
        article_no      TEXT                         /* 货号 */,
        length_cm       REAL                         /* 衣长 */,
        chest_cm        REAL                         /* 胸围 */,
        shoulder_cm     REAL                         /* 肩宽 */,
        size_label      TEXT                         /* 对应尺码 */,
        purchase_date   TEXT                         /* 购买日期 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 长袖 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS long_sleeve (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        brand           TEXT NOT NULL                /* 品牌 */,
        model           TEXT                         /* 型号 */,
        color           TEXT                         /* 配色 */,
        article_no      TEXT                         /* 货号 */,
        length_cm       REAL                         /* 衣长 */,
        chest_cm        REAL                         /* 胸围 */,
        shoulder_cm     REAL                         /* 肩宽 */,
        size_label      TEXT                         /* 对应尺码 */,
        purchase_date   TEXT                         /* 购买日期 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 短裤 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shorts (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        brand           TEXT NOT NULL                /* 品牌 */,
        model           TEXT                         /* 型号 */,
        color           TEXT                         /* 配色 */,
        article_no      TEXT                         /* 货号 */,
        length_cm       REAL                         /* 裤长 */,
        waist_cm        REAL                         /* 腰围 */,
        hip_cm          REAL                         /* 臀围 */,
        size_label      TEXT                         /* 对应尺码 */,
        purchase_date   TEXT                         /* 购买日期 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 长裤 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS trousers (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        brand           TEXT NOT NULL                /* 品牌 */,
        model           TEXT                         /* 型号 */,
        color           TEXT                         /* 配色 */,
        article_no      TEXT                         /* 货号 */,
        length_cm       REAL                         /* 裤长 */,
        waist_cm        REAL                         /* 腰围 */,
        hip_cm          REAL                         /* 臀围 */,
        size_label      TEXT                         /* 对应尺码 */,
        purchase_date   TEXT                         /* 购买日期 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 袜子 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS socks (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        brand           TEXT NOT NULL                /* 品牌 */,
        model           TEXT                         /* 型号 */,
        color           TEXT                         /* 配色 */,
        article_no      TEXT                         /* 货号 */,
        size_label      TEXT                         /* 尺码 */,
        purchase_date   TEXT                         /* 购买日期 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 鞋 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shoes (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        brand           TEXT NOT NULL                /* 品牌 */,
        model           TEXT                         /* 型号 */,
        color           TEXT                         /* 配色 */,
        article_no      TEXT                         /* 货号 */,
        mm_size         TEXT                         /* mm */,
        eur_size        TEXT                         /* EUR */,
        purchase_date   TEXT                         /* 购买日期 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 汽车模型 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS car_models (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        scale           TEXT                         /* 实车比例(如1:18) */,
        real_brand      TEXT                         /* 实车品牌 */,
        real_model      TEXT                         /* 实车型号 */,
        color           TEXT                         /* 配色 */,
        model_brand     TEXT                         /* 模型品牌 */,
        purchase_date   TEXT                         /* 购买日期 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 驾驶经历 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS driving_experience (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        year            TEXT                         /* 年份 */,
        model           TEXT                         /* 型号 */,
        version         TEXT                         /* 版本 */,
        drivetrain      TEXT                         /* 驱动形式 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    # ── 电子设备 ──
    cur.execute("""
    CREATE TABLE IF NOT EXISTS electronics (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        category        TEXT NOT NULL                /* 类别: 手机/平板/手表/耳机 */,
        brand           TEXT NOT NULL                /* 品牌 */,
        model           TEXT                         /* 型号 */,
        color           TEXT                         /* 配色 */,
        release_date    TEXT                         /* 发布日期 */,
        purchase_date   TEXT                         /* 购买日期 */,
        status          TEXT NOT NULL DEFAULT '使用中' /* 状态: 使用中/闲置中/已出售/已损坏 */,
        image_path      TEXT                         /* 图片路径 */,
        created_at      TEXT DEFAULT (datetime('now', 'localtime'))
    )""")

    conn.commit()
    cur.close()
    conn.close()
    print(f"[OK] 数据库 `{DB_PATH}` 初始化完成")


if __name__ == "__main__":
    init_database()
