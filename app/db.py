# app/db.py
import sqlite3
from flask import g, current_app

_SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    id        INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL UNIQUE,
    capacity  INTEGER NOT NULL,
    equipment TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS reservations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id    INTEGER NOT NULL,
    user_name  TEXT    NOT NULL,
    user_email TEXT    NOT NULL,
    date       TEXT    NOT NULL,
    start_time TEXT    NOT NULL,
    end_time   TEXT    NOT NULL,
    purpose    TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);
"""


def _dict_factory(cursor, row):
    if not cursor.description:
        return row
    return dict(zip([col[0] for col in cursor.description], row))


class _SQLiteWrapper:
    """sqlite3.Connection wrapper — accepts cursor(dictionary=...) like mariadb."""

    def __init__(self, path):
        self._conn = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self._conn.row_factory = _dict_factory
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(_SQLITE_SCHEMA)

    def cursor(self, dictionary=False):
        return self._conn.cursor()

    def close(self):
        self._conn.close()


def _connect_mariadb(app):
    import mariadb
    return mariadb.connect(
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME'],
        port=app.config['DB_PORT'],
        autocommit=True,
    )


def get_db():
    if 'db' not in g:
        app = current_app._get_current_object()
        try:
            g.db = _connect_mariadb(app)
        except Exception:
            db_path = app.config.get('SQLITE_DB_PATH', 'seminar.db')
            g.db = _SQLiteWrapper(db_path)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
