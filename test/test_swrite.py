import shutil
import copy
import tempfile
import io
import os
from pathlib import Path
from typing import Tuple
import pytest
from collections.abc import Generator
from scrummd.config import ScrumConfig
from scrummd.card import from_str
from scrummd.collection import get_collection, Collection
from scrummd.swrite import entry
from fixtures import data_config, test_collection


@pytest.fixture(scope="function")
def modifiable_on_disk_collection(
    data_config,
) -> Generator[Tuple[Collection, ScrumConfig]]:
    """
    Copies the test fixture collection to a temp folder, and returns a
    tuple of the config and collection.
    """
    old_path = os.getcwd()
    try:
        with tempfile.TemporaryDirectory() as tdir:
            config = copy.copy(data_config)
            path = str(Path(tdir) / "test_collection")
            config.scrum_path = path
            shutil.copytree("test/data", path)
            os.chdir(path)
            print(f"CHANGE TO {path}")
            yield (get_collection(config), config)
    finally:
        os.chdir(old_path)


def test_swrite_field(modifiable_on_disk_collection, data_config):
    """End to end test setting a field with swrite"""
    config = modifiable_on_disk_collection[1]

    entry(["c1", "--set", "assignee", "Scotty"], config=config)

    read_collection = get_collection(modifiable_on_disk_collection[1])
    assert (
        read_collection["c1"].udf["assignee"] == "Scotty"
    ), "Field was not changed in file"


def test_swrite_field_stdout(modifiable_on_disk_collection, data_config):
    """End to end test setting a field with swrite, writing to stdout"""

    out_stream = io.StringIO()
    config = modifiable_on_disk_collection[1]

    entry(["c1", "--set", "assignee", "Scotty", "-o"], stdout=out_stream, config=config)

    read_collection = get_collection(config)
    read_card = read_collection["c1"]
    assert read_card.udf["assignee"] == "Bob", "File was incorrectly overwitten"

    out_stream.seek(0)
    card_from_stdio = from_str(
        config,
        out_stream.read(),
        read_card.collection_from_path,
        Path(read_card.path),
    )

    assert card_from_stdio.udf["assignee"] == "Scotty", "Field was not changed in stdio"


def test_swrite_field_stdin(test_collection, data_config):
    """End to end test setting a field with a value from stdin"""

    out_stream = io.StringIO()
    new_description = "Space.\\nThe Final Frontier."
    in_stream = io.StringIO(new_description)
    entry(
        ["c1", "--set-stdin", "description", "-o"],
        stdout=out_stream,
        stdin=in_stream,
        config=data_config,
    )

    read_card = test_collection["c1"]

    out_stream.seek(0)
    card_from_stdio = from_str(
        data_config,
        out_stream.read(),
        read_card.collection_from_path,
        Path(read_card.path),
    )

    assert card_from_stdio.udf["description"] == new_description


def test_swrite_add_to_list(test_collection, data_config):
    """End to end test adding a value to a list"""

    out_stream = io.StringIO()
    entry(
        ["c5", "-o", "--add", "tags", "new tag"],
        stdout=out_stream,
        config=data_config,
    )
    out_stream.seek(0)
    read_card = test_collection["c5"]
    card_from_stdio = from_str(
        data_config,
        out_stream.read(),
        read_card.collection_from_path,
        Path(read_card.path),
    )

    assert card_from_stdio.udf["tags"] == ["special2", "special", "special3", "new tag"]


def test_swrite_remove_from_list(test_collection, data_config):
    """End to end test removing a value from a list"""

    out_stream = io.StringIO()
    entry(
        ["-o", "c5", "-r", "tags", "special"],
        stdout=out_stream,
        config=data_config,
    )
    out_stream.seek(0)
    read_card = test_collection["c5"]
    card_from_stdio = from_str(
        data_config,
        out_stream.read(),
        read_card.collection_from_path,
        Path(read_card.path),
    )

    assert card_from_stdio.udf["tags"] == ["special2", "special3"]


def test_swrite_multiple_operations(test_collection, data_config):
    """End to end test add to list, remove from list, modify other field."""

    out_stream = io.StringIO()
    entry(
        [
            "-o",
            "c5",
            "-r",
            "tags",
            "special",
            "-s",
            "estimate",
            "3",
            "-a",
            "tags",
            "new",
        ],
        stdout=out_stream,
        config=data_config,
    )
    out_stream.seek(0)
    read_card = test_collection["c5"]
    card_from_stdio = from_str(
        data_config,
        out_stream.read(),
        read_card.collection_from_path,
        Path(read_card.path),
    )

    assert card_from_stdio.udf["tags"] == ["special2", "special3", "new"]
    assert card_from_stdio.udf["estimate"] == 3
