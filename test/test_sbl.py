import os
import pytest
from scrummd import const
import scrummd.sbl
import tempfile
from pathlib import Path


@pytest.fixture(scope="function")
def temp_dir():
    with tempfile.TemporaryDirectory() as td:
        while not os.path.exists(td):
            pass
        os.chdir(td)
        yield td


@pytest.fixture(scope="function")
def pyproject_with_config(temp_dir):
    with open(Path(temp_dir, "pyproject.toml"), "w") as fo:
        fo.write(PYPROJECT_WITH_CONFIG)
        fo.flush()
        yield


@pytest.fixture(scope="function")
def pyproject_without_config(temp_dir):
    with open(Path(temp_dir, "pyproject.toml"), "w") as fo:
        fo.write(PYPROJECT_WITHOUT_CONFIG)
        fo.flush()
        yield


@pytest.fixture(scope="function")
def scrum_dot_toml(temp_dir):
    with open(Path(temp_dir, "scrum.toml"), "w") as fo:
        fo.write(BASIC_TOOL_ONLY)
        fo.flush()
        yield


PYPROJECT_WITHOUT_CONFIG = """[project]
name = "scrummd"
scrum_path = "no_config"
"""

PYPROJECT_WITH_CONFIG = """[project]
name = "scrummd"

[tool.scrummd]
strict = true
scrum_path = "with_config"
"""

BASIC_TOOL_ONLY = """
[tool.scrummd]
strict = true
scrum_path = "basic_tool"
"""


def test_no_file(temp_dir):
    """Test that defaults are used where no config"""
    config = scrummd.sbl.load_fs_config()
    assert config.scrum_path == const.DEFAULT_SCRUM_FOLDER_NAME


def test_priority(temp_dir, scrum_dot_toml, pyproject_with_config):
    """Test the priority order of which config works"""
    config = scrummd.sbl.load_fs_config()
    assert config.scrum_path == "basic_tool"


def test_with_configless_pyproject(temp_dir, pyproject_without_config):
    """Test that default is used when only pyproject is there and not config in it"""
    config = scrummd.sbl.load_fs_config()
    assert config.scrum_path == const.DEFAULT_SCRUM_FOLDER_NAME


def test_with_config_pyproject(temp_dir, pyproject_with_config):
    """Test that the tool works when pyproject is laid out as normal"""
    config = scrummd.sbl.load_fs_config()
    assert config.scrum_path == "with_config"
