import pytest
import tempfile
import pathlib
from scrummd.cache import Cache
import scrummd.exceptions
import scrummd.config


@pytest.fixture(scope="function")
def cache_randomized_config():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield scrummd.config.ScrumConfig(
            cache_file=pathlib.Path(temp_dir).joinpath(".cache.sqlite3")
        )


def test_new_with_existing_cache_file(cache_randomized_config):
    cache = Cache(cache_randomized_config.cache_file)
    cache._init_new_db()
    cache2 = Cache(cache_randomized_config.cache_file)
    pytest.raises(
        scrummd.exceptions.DbAlreadyExistsError, lambda: cache2._init_new_db()
    )
