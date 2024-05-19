from enum import Enum, auto
import os
from pathlib import Path
import sqlite3
import logging
from typing import NamedTuple

from scrummd.config import ScrumConfig
from scrummd.exceptions import DbAlreadyExistsError

logger = logging.getLogger(__name__)

CREATE_DB_SQL = """
    CREATE TABLE "processed_files" ("path", "last_modified");
    CREATE TABLE "current_files" ("path", "last_modified");
"""


class ChangeType(Enum):
    MODIFIED = auto()
    CREATED = auto()
    DELETED = auto()


class ChangedFile(NamedTuple):
    operation: ChangeType
    path: Path


class Cache:
    def __init__(self, config: ScrumConfig, force_in_memory: bool = False):
        self.path = config.cache_file
        self.force_in_memory = force_in_memory
        self.config = config
        self._db = None

    def db(self):
        if self._db:
            return self._db

        effective_path = ":memory:" if self.force_in_memory else self.config.cache_file
        self._db = sqlite3.connect(effective_path)
        return self._db

    def _init_new_db(self):
        """Initialize the DB from scratch"""

        empty_cursor = self.db().execute("SELECT name FROM sqlite_master")
        if len(empty_cursor.fetchall()) > 0:
            raise DbAlreadyExistsError()

        self.db().executescript(CREATE_DB_SQL)

    def _update_current_files(self):
        """Get current files from the os and update the table"""
        for root, _, files in os.walk(self.config.scrum_path, followlinks=True):
            paths = Path(root).joinpath()

    def get_file_changes(self) -> set[ChangedFile]:
        return set()


def get_cache(scrum_config: ScrumConfig) -> Cache:
    """Get (from the filesystem), or create, a cache

    Args:
        scrum_config (ScrumConfig): Scrum configuration

    Returns:
        Cache: Cache object that can be used
    """
    return Cache(scrum_config)
