import sqlite3
from typing import Optional

from scrummd.config import ScrumConfig
from scrummd.exceptions import DbAlreadyExistsError

CREATE_DB_SQL = """
    CREATE TABLE "files" ("index")
"""


class Cache:
    def __init__(self, path: Optional[str]):
        self.path = path

    def _init_new_db(self):
        """Initialize the DB from scratch"""
        effective_path = self.path or ":memory:"
        db = sqlite3.connect(effective_path)

        empty_cursor = db.execute("SELECT name FROM sqlite_master")
        if len(empty_cursor.fetchall()) > 0:
            raise DbAlreadyExistsError()

        db.execute(CREATE_DB_SQL)


def get_cache(scrum_config: ScrumConfig) -> Cache:
    """Get (from the filesystem), or create, a cache

    Args:
        scrum_config (ScrumConfig): Scrum configuration

    Returns:
        Cache: Cache object that can be used
    """
    return Cache(None)
