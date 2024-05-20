import sqlite3
import pytest
import tempfile
from pathlib import Path
import random
import os
import time
from scrummd.cache import Cache, ChangeType, ChangedFile
import scrummd.exceptions
import scrummd.config
import scrummd.version


@pytest.fixture(scope="function")
def temp_scrum_directory():
    working_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        yield tmpdir
    os.chdir(working_dir)


@pytest.fixture(scope="function")
def scrum_cached_config(temp_scrum_directory):
    print(temp_scrum_directory)
    yield scrummd.config.ScrumConfig(
        cache_file=Path(temp_scrum_directory).joinpath(".cache.sqlite3"),
        config_metadata=scrummd.config.ConfigMetadata(1000, "config"),
    )


def rand_str(size: int, whitespace: bool = False):
    return "".join(
        [
            random.choice(
                f"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ{' ' if whitespace else ''}"
            )
            for _ in range(size)
        ]
    )


SCRUM_CARD_COUNT = 10
"""Amount of random cards per folder for randomized scrum cards to create"""

FOLDER_DEPTH = 3
"""Folder depth to create cards into"""

FOLDER_COUNT = 3
"""Amount of folders to create in each folder"""

card_number = 0


@pytest.fixture(scope="function")
def randomized_scrum_cards(temp_scrum_directory, scrum_cached_config) -> list[Path]:
    scrum_dir = Path(temp_scrum_directory, scrum_cached_config.scrum_path)
    os.mkdir(scrum_dir)
    return create_cards_folder(
        FOLDER_DEPTH,
        scrum_dir,
        temp_scrum_directory,
    )


def create_cards_folder(levels_remaining: int, folder_path: Path, root_path: Path):
    paths: list[Path] = []
    global card_number
    for _ in range(SCRUM_CARD_COUNT):
        card_number += 1
        new_card_path = Path(folder_path, f"c{card_number}.md")
        paths.append(new_card_path.relative_to(root_path))
        create_card(new_card_path)

    if levels_remaining > 0:
        for _ in range(FOLDER_COUNT):
            folder_path = Path(folder_path).joinpath(rand_str(8))
            os.mkdir(folder_path)
            paths.extend(
                create_cards_folder(levels_remaining - 1, folder_path, root_path)
            )

    return paths


def create_card(path: Path):
    # Currently, just creates a 'summary'. Will add more as needed later.
    with open(path, "w") as card_f:
        contents = f"---\n summary: {rand_str(20)}\n---"
        card_f.write(contents)


def test_get_file_changes_new_cache(
    temp_scrum_directory, scrum_cached_config, randomized_scrum_cards
):
    """Test that get_file_changes returns all the files as added in a new cache"""
    cache = Cache(scrum_cached_config)
    changes = cache.get_file_changes()

    assert changes == {
        ChangedFile(ChangeType.CREATED, path) for path in randomized_scrum_cards
    }


FILES_TO_DELETE = 10


def test_get_file_changes_deleted_files(
    temp_scrum_directory, scrum_cached_config, randomized_scrum_cards
):
    """Test that get_file_changes returns the deleted files when deleted"""
    cache = Cache(scrum_cached_config)
    cache.get_file_changes()

    deleted_files = {
        random.choice(randomized_scrum_cards) for _ in range(FILES_TO_DELETE)
    }
    for file_to_delete in deleted_files:
        os.remove(Path(temp_scrum_directory, file_to_delete))

    changes = cache.get_file_changes()

    assert changes == {ChangedFile(ChangeType.DELETED, path) for path in deleted_files}


def test_get_file_changes_modified_files(
    temp_scrum_directory, scrum_cached_config, randomized_scrum_cards
):
    """Test that get_file_changes returns the deleted files when deleted"""
    cache = Cache(scrum_cached_config)
    cache.get_file_changes()

    # Make sure modified time is different
    # Modified time has resolution of 1s on Mac, up to 2s on Windows. Multiple
    # values on Linux.
    time.sleep(2.1)

    changed_files = {
        random.choice(randomized_scrum_cards) for _ in range(FILES_TO_DELETE)
    }
    for file_to_change in changed_files:
        with open(Path(temp_scrum_directory, file_to_change), "a") as f:
            f.write(f"# {rand_str(5)}\n\n{rand_str(10)}")

    changes = cache.get_file_changes()

    assert changes == {ChangedFile(ChangeType.MODIFIED, path) for path in changed_files}


@pytest.fixture(scope="function")
def restore_version():
    old_version = scrummd.version.version
    yield
    scrummd.version.version = old_version


def test_cache_invalidation_version(
    temp_scrum_directory, scrum_cached_config, restore_version
):
    """Test that cache is invalidated when version changes"""

    cache = Cache(scrum_cached_config)
    cache.update_metadata()

    scrummd.version.version = "new"

    effective_path = scrum_cached_config.cache_file
    db = sqlite3.connect(effective_path)
    cache2 = Cache(scrum_cached_config)
    assert cache2.cache_invalidated(db)


def test_cache_invalidation_no_change(
    temp_scrum_directory, scrum_cached_config, restore_version
):
    """Test that cache is not invalidated when version and config doesn't change"""

    cache = Cache(scrum_cached_config)
    cache.update_metadata()

    effective_path = scrum_cached_config.cache_file
    db = sqlite3.connect(effective_path)
    cache2 = Cache(scrum_cached_config)
    assert not cache2.cache_invalidated(db)


def test_cache_invalidation_config_modified_time(
    temp_scrum_directory, scrum_cached_config, restore_version
):
    """Test that cache is invalidated when config modified changes"""

    cache = Cache(scrum_cached_config)
    cache.update_metadata()

    modified_config = scrummd.config.ScrumConfig(
        cache_file=scrum_cached_config,
        config_metadata=scrummd.config.ConfigMetadata(
            999999, scrum_cached_config.config_metadata.path
        ),
    )

    effective_path = scrum_cached_config.cache_file
    db = sqlite3.connect(effective_path)
    cache2 = Cache(modified_config)
    assert cache2.cache_invalidated(db)


def test_cache_invalidation_config_modified_path(
    temp_scrum_directory, scrum_cached_config, restore_version
):
    """Test that cache is invalidated when config modified changes"""

    cache = Cache(scrum_cached_config)
    cache.update_metadata()

    modified_config = scrummd.config.ScrumConfig(
        cache_file=scrum_cached_config,
        config_metadata=scrummd.config.ConfigMetadata(
            scrum_cached_config.config_metadata.modified_time, "new path.config"
        ),
    )

    effective_path = scrum_cached_config.cache_file
    db = sqlite3.connect(effective_path)
    cache2 = Cache(modified_config)
    assert cache2.cache_invalidated(db)
