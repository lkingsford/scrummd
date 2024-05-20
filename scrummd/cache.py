from enum import Enum, auto
import os
from pathlib import Path
import sqlite3
import logging
from typing import NamedTuple, Optional

import scrummd.version
from scrummd.config import ScrumConfig

logger = logging.getLogger(__name__)

"""
    cache_data - data on the cache itself, used to check if invalid
    processed_file - the file as they are in the db
    current_file - the file as they are in the fileystem
"""
CREATE_DB_SQL = """
    CREATE TABLE "cache_data" ("config_last_modified", "config_filename", "scrummd_version");
    CREATE TABLE "processed_file" ("path", "last_modified");
    CREATE TABLE "current_file" ("path", "last_modified");
"""


class ChangeType(Enum):
    """Type of change in ChangedFile"""

    MODIFIED = auto()
    CREATED = auto()
    DELETED = auto()


class ChangedFile(NamedTuple):
    """Output for get_file_changes"""

    operation: ChangeType
    """What happened to the file"""
    path: Path
    """Path of the file"""


def _deep_scan(path, max_depth=100) -> list[os.DirEntry]:
    """Return all the scan values recursively for a folder

    Args:
        path (_type_): The path the scan

    Returns:
        list[os.DirEntry]: The list of scanned entries
    """
    if max_depth == 0:
        # Short circuit - you know, just in case of stupid things being done
        # with a fileystem
        return []

    scan_results = list(os.scandir(path))
    dirs = [p for p in scan_results if p.is_dir()]
    file = [p for p in scan_results if p.is_file()]
    for entry in dirs:
        file.extend(_deep_scan(entry.path, max_depth - 1))
    return file


class Cache:
    def __init__(self, config: ScrumConfig, force_in_memory: bool = False):
        self.path = config.cache_file
        self.force_in_memory = force_in_memory
        self.config = config
        self._db: Optional[sqlite3.connection] = None

    def db(self) -> sqlite3.Connection:
        if self._db:
            return self._db

        effective_path = ":memory:" if self.force_in_memory else self.config.cache_file
        self._db = sqlite3.connect(effective_path)
        invalidated = self.cache_invalidated(self._db)
        if invalidated:
            self._init_new_db()
        self.update_metadata()
        return self._db

    def _init_new_db(self):
        """Initialize the DB from scratch"""

        # First, drop any existing tables
        tables_cursor = self.db().execute(
            """SELECT "name" FROM "sqlite_master" WHERE type="table";"""
        )
        existing_tables = tables_cursor.fetchall()
        for table_name in existing_tables:
            # Do not like string here! Parameters can't work for table names.
            self.db().execute(f"DROP TABLE {table_name[0]};")

        # And create it anew
        self.db().executescript(CREATE_DB_SQL)
        self.db().commit()

    def _update_current_files(self):
        """Get current file from the os and update the table"""
        scan_results = _deep_scan(self.config.scrum_path)
        current_file_data = [(f.path, f.stat().st_mtime_ns) for f in scan_results]
        self.db().execute("""DELETE FROM "current_file" """)
        self.db().executemany(
            """INSERT INTO "current_file" VALUES (?, ?)""", current_file_data
        )

    def get_file_changes(self) -> set[ChangedFile]:
        results: set[ChangedFile] = set()
        self._update_current_files()

        added_cursor = self.db().execute(
            """SELECT "path" FROM "current_file" WHERE "path" NOT IN (SELECT "path" FROM "processed_file") """
        )
        for row in added_cursor:
            results.add(ChangedFile(ChangeType.CREATED, Path(row[0])))

        removed_cursor = self.db().execute(
            """SELECT "path" FROM "processed_file" WHERE "path" NOT IN (SELECT "path" FROM "current_file") """
        )
        for row in removed_cursor:
            results.add(ChangedFile(ChangeType.DELETED, Path(row[0])))

        modified_cursor = self.db().execute(
            """SELECT "current_file"."path" FROM "current_file" LEFT JOIN "processed_file" ON "current_file"."path" = "processed_file"."path" WHERE "current_file"."last_modified" != "processed_file"."last_modified" """
        )
        for row in modified_cursor:
            results.add(ChangedFile(ChangeType.MODIFIED, Path(row[0])))

        # This will be when the file is read into the DB later - but, we need
        # it for now to detect changes
        self.db().execute("""DELETE FROM "processed_file" """)
        self.db().execute(
            """INSERT INTO "processed_file" SELECT * FROM "current_file" """
        )
        self.db().commit()
        return results

    def cache_invalidated(self, db: sqlite3.Connection) -> bool:
        """Check if cache is invalidated

        The cache is invalidated if there is a new version of ScrumMD, or there
        is an update to the config file.

        Args:
            db: Database connection to use

        Returns:
            bool: True if the cache needs to be rebuilt.
        """
        # db is an argument so it can be used by the db() function
        meta_exists_cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cache_data';"
        )
        if not meta_exists_cursor.fetchone():
            return True
        result = False
        version_cursor = db.execute(
            """SELECT "config_last_modified", "config_filename", "scrummd_version" FROM "cache_data" """
        )
        version_data = version_cursor.fetchone()
        if version_data:
            cache_config_last_modified, cache_config_filename, cache_scrummd_version = (
                version_data
            )

            if cache_scrummd_version != scrummd.version.version:
                logging.info("Cache invalidated - new ScrumMD version")
                return True

            if (
                cache_config_last_modified != self.config.config_metadata.modified_time
                or cache_config_filename != self.config.config_metadata.path
            ):
                logging.info("Cache invalidated - config file modified")
                return True
        else:
            logging.info("Cache invalidated - no previous metadata")
            result = True

        return False

    def update_metadata(self) -> None:
        self.db().execute("""DELETE FROM "cache_data" """)
        self.db().execute(
            """INSERT INTO "cache_data" ("config_last_modified", "config_filename", "scrummd_version")  VALUES (?, ?, ?) """,
            (
                self.config.config_metadata.modified_time,
                self.config.config_metadata.path,
                scrummd.version.version,
            ),
        )
        self.db().commit()


def get_cache(scrum_config: ScrumConfig) -> Cache:
    """Get (from the fileystem), or create, a cache

    Args:
        scrum_config (ScrumConfig): Scrum configuration

    Returns:
        Cache: Cache object that can be used
    """
    return Cache(scrum_config)
