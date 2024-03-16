import os
import pytest
from scrummd import const
from scrummd.config_loader import load_fs_config
import tempfile
from pathlib import Path


@pytest.fixture(scope="function")
def temp_dir():
    initial_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        while not os.path.exists(td):
            pass
        os.chdir(td)
        yield td
    os.chdir(initial_dir)


PYPROJECT_WITH_CONFIG = """[project]
name = "scrummd"

[tool.scrummd]
strict = true
scrum_path = "with_config"
"""


@pytest.fixture(scope="function")
def pyproject_with_config(temp_dir):
    with open(Path(temp_dir, "pyproject.toml"), "w") as fo:
        fo.write(PYPROJECT_WITH_CONFIG)
        fo.flush()
        yield


PYPROJECT_WITHOUT_CONFIG = """[project]
name = "scrummd"
scrum_path = "no_config"
"""


@pytest.fixture(scope="function")
def pyproject_without_config(temp_dir):
    with open(Path(temp_dir, "pyproject.toml"), "w") as fo:
        fo.write(PYPROJECT_WITHOUT_CONFIG)
        fo.flush()
        yield


BASIC_TOOL_ONLY = """
[tool.scrummd]
strict = true
scrum_path = "basic_tool"

[tool.scrummd.fields]
status = ["Ready", "Progress", "Done"]
"""


@pytest.fixture(scope="function")
def scrum_dot_toml(temp_dir):
    with open(Path(temp_dir, "scrum.toml"), "w") as fo:
        fo.write(BASIC_TOOL_ONLY)
        fo.flush()
        yield


def test_no_file(temp_dir):
    """Test that defaults are used where no config"""
    config = load_fs_config()
    assert config.scrum_path == const.DEFAULT_SCRUM_FOLDER_NAME


def test_priority(temp_dir, scrum_dot_toml, pyproject_with_config):
    """Test the priority order of which config works"""
    config = load_fs_config()
    assert config.scrum_path == "basic_tool"


def test_with_configless_pyproject(temp_dir, pyproject_without_config):
    """Test that default is used when only pyproject is there and not config in it"""
    config = load_fs_config()
    assert config.scrum_path == const.DEFAULT_SCRUM_FOLDER_NAME


def test_with_config_pyproject(temp_dir, pyproject_with_config):
    """Test that the tool works when pyproject is laid out as normal"""
    config = load_fs_config()
    assert config.scrum_path == "with_config"


def test_fields_table(temp_dir, scrum_dot_toml):
    """Test that the fields values are set from tool.scrummd.field"""
    config = load_fs_config()
    assert config.fields["status"] == ["Ready", "Progress", "Done"]


COLLECTION_CONFIG = """
[tool.scrummd]
strict = true
scrum_path = "basic_tool"

[tool.scrummd.fields]
status = ["Ready", "Progress", "Done"]

[tool.scrummd.collections.epic]
required = ["cost", "components"]

[tool.scrummd.collections.epic.fields]
status = ["Not Defined", "Started", "Done"]
"""


@pytest.fixture(scope="function")
def collection_config_f(temp_dir):
    with open(Path(temp_dir, "scrum.toml"), "w") as fo:
        fo.write(COLLECTION_CONFIG)
        fo.flush()
        yield


def test_collection_level_1(temp_dir, collection_config_f):
    """Test that a setting in [tool.scrummd.collections.*] is set"""
    config = load_fs_config()
    assert config.collections["epic"].required == ["cost", "components"]


def test_collection_level_2(temp_dir, collection_config_f):
    """Test that a setting in [tool.scrummd.collections.*.fields] is set"""
    config = load_fs_config()
    assert config.collections["epic"].fields["status"] == [
        "Not Defined",
        "Started",
        "Done",
    ]
