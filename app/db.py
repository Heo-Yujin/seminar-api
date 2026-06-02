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
INSERT OR IGNORE INTO rooms (id, name, capacity, equipment) VALUES
(1,  'Grand Hall A',     180, NULL),
(2,  'Grand Hall B',     165, NULL),
(3,  'Grand Hall C',     150, NULL),
(4,  'Grand Hall D',     140, NULL),
(5,  'Grand Hall E',     132, NULL),
(6,  'Summit Room 1',     96, NULL),
(7,  'Summit Room 2',     90, NULL),
(8,  'Summit Room 3',     84, NULL),
(9,  'Summit Room 4',     78, NULL),
(10, 'Forum Room 1',      72, NULL),
(11, 'Forum Room 2',      66, NULL),
(12, 'Forum Room 3',      60, NULL),
(13, 'Forum Room 4',      56, NULL),
(14, 'Studio Room 1',     52, NULL),
(15, 'Studio Room 2',     48, NULL),
(16, 'Studio Room 3',     44, NULL),
(17, 'Studio Room 4',     40, NULL),
(18, 'Workshop Room 1',   36, NULL),
(19, 'Workshop Room 2',   34, NULL),
(20, 'Workshop Room 3',   32, NULL),
(21, 'Workshop Room 4',   30, NULL),
(22, 'Meeting Room 1',    28, NULL),
(23, 'Meeting Room 2',    26, NULL),
(24, 'Meeting Room 3',    24, NULL),
(25, 'Meeting Room 4',    22, NULL),
(26, 'Focus Room 1',      18, NULL),
(27, 'Focus Room 2',      16, NULL),
(28, 'Focus Room 3',      14, NULL),
(29, 'Focus Room 4',      12, NULL),
(30, 'Focus Room 5',      10, NULL);
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
