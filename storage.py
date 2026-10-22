"""Shared PostgreSQL on Vercel; SQLite is available only for local development."""
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parent
class ConfigurationError(RuntimeError):
    pass

class Connection:
    def __init__(self, raw, postgres):
        self.raw, self.postgres = raw, postgres
    def execute(self, sql, args=()):
        return self.raw.execute(sql.replace('?', '%s') if self.postgres else sql, args)

@contextmanager
def database():
    url = os.environ.get('DATABASE_URL', '').strip()
    if url:
        if not url.startswith(('postgres://', 'postgresql://')):
            raise ConfigurationError('DATABASE_URL must be a PostgreSQL connection URL.')
        import psycopg
        from psycopg.rows import dict_row
        raw = psycopg.connect(url, row_factory=dict_row, connect_timeout=10, prepare_threshold=None, client_encoding='utf8')
    else:
        if os.environ.get('VERCEL'):
            raise ConfigurationError('Set DATABASE_URL to a persistent PostgreSQL database before using the app on Vercel.')
        path = Path(os.environ.get('LOCAL_DATABASE_PATH', str(ROOT/'data'/'local.sqlite3')))
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = sqlite3.connect(path, timeout=15)
        raw.row_factory = sqlite3.Row
        raw.execute('PRAGMA foreign_keys=ON')
    try:
        yield Connection(raw, bool(url))
        raw.commit()
    except BaseException:
        raw.rollback()
        raise
    finally:
        raw.close()

def _migrate_level_range(db):
    # Older databases capped zs_completions at level 4; widen to 7 in place.
    if db.postgres:
        rows = db.execute("SELECT conname, pg_get_constraintdef(oid) AS def FROM pg_constraint WHERE conrelid='zs_completions'::regclass AND contype='c'").fetchall()
        widened = False
        for row in rows:
            definition = row['def'] or ''
            if 'level_id' in definition and '7' in definition:
                widened = True
            elif 'level_id' in definition:
                db.execute('ALTER TABLE zs_completions DROP CONSTRAINT "' + row['conname'].replace('"','""') + '"')
        if not widened:
            db.execute('ALTER TABLE zs_completions ADD CONSTRAINT zs_completions_level_range CHECK(level_id BETWEEN 1 AND 7)')
    else:
        row = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='zs_completions'").fetchone()
        if row and row['sql'] and 'BETWEEN 1 AND 4' in row['sql']:
            db.execute('''CREATE TABLE zs_completions_new (
                entry_id TEXT NOT NULL REFERENCES zs_entries(id) ON DELETE CASCADE,
                level_id INTEGER NOT NULL CHECK(level_id BETWEEN 1 AND 7),
                completed_at DOUBLE PRECISION NOT NULL,
                PRIMARY KEY(entry_id,level_id))''')
            db.execute('INSERT INTO zs_completions_new(entry_id,level_id,completed_at) SELECT entry_id,level_id,completed_at FROM zs_completions')
            db.execute('DROP TABLE zs_completions')
            db.execute('ALTER TABLE zs_completions_new RENAME TO zs_completions')

def initialize():
    with database() as db:
        for statement in (ROOT/'schema.sql').read_text().split(';'):
            if statement.strip():
                db.execute(statement)
        _migrate_level_range(db)

if __name__ == '__main__':
    initialize()
    print('Database schema is ready. No existing students or progress were deleted.')
