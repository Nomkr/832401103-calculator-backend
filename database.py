"""
database.py —— 计算器的"仓库管理员"。

这个文件负责跟 SQLite 数据库打交道：存历史、查历史、删历史。
数据库就是一个文件（calculator.db），存在本文件同目录下。

对外提供 5 个函数：
    init_db()              建表（第一次运行时调用）
    add_history(expr, res) 存一条历史
    get_history()          查所有历史（新的在前）
    delete_history(id)     删一条历史
    clear_history()        清空全部历史（加分项）
"""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime

# 数据库文件的完整路径：固定放在本文件同目录下，无论从哪里运行都不会跑偏。
# __file__ 是"当前这个文件的路径"，os.path.dirname 取它所在的文件夹。
DB_FILE = os.getenv(
    "CALCULATOR_DB_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "calculator.db"),
)


def get_connection():
    """打开数据库连接（相当于拿钥匙进仓库）。"""
    db_dir = os.path.dirname(os.path.abspath(DB_FILE))
    os.makedirs(db_dir, exist_ok=True)
    # timeout 防止多个请求短时间写入时立即报 database is locked。
    conn = sqlite3.connect(DB_FILE, timeout=5)
    # 让查询结果能"按列名"取值，方便后面转成字典
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def db_session():
    """提供一个自动提交、异常回滚并始终关闭的数据库会话。"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """建表。CREATE TABLE IF NOT EXISTS = 表不存在才建，存在就跳过。"""
    with db_session() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculation_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result     TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def add_history(expression, result):
    """存一条历史。INSERT INTO ... VALUES (?, ?, ?) 里的 ? 是"占位符"。"""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 当前时间，格式如 2026-10-03 10:20:00
    with db_session() as conn:
        conn.execute(
            "INSERT INTO calculation_history (expression, result, created_at) VALUES (?, ?, ?)",
            (expression, str(result), created_at),
        )


def get_history():
    """查所有历史。ORDER BY id DESC = 按 id 倒序，新的在前面。"""
    with db_session() as conn:
        rows = conn.execute(
            "SELECT id, expression, result, created_at FROM calculation_history ORDER BY id DESC"
        ).fetchall()
    # 把每一行转成字典，方便 app.py 直接转成 JSON 返回给前端
    return [dict(row) for row in rows]


def delete_history(history_id):
    """删一条历史。WHERE id = ? 表示只删 id 匹配的那一行。"""
    with db_session() as conn:
        cursor = conn.execute("DELETE FROM calculation_history WHERE id = ?", (history_id,))
        deleted = cursor.rowcount > 0
    return deleted


def clear_history():
    """清空全部历史（加分项）。"""
    with db_session() as conn:
        conn.execute("DELETE FROM calculation_history")


# 直接运行本文件时，执行下面的测试
if __name__ == "__main__":
    init_db()
    add_history("1+2", 3)
    add_history("(2+3)*4", 20)

    print("全部历史（新的在前）：")
    for row in get_history():
        print(row)

    # 删除最新那条
    latest = get_history()[0]
    delete_history(latest["id"])
    print("删除最新一条后：")
    for row in get_history():
        print(row)
