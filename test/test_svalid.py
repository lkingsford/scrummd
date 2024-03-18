from copy import copy
from scrummd.svalid import get_exit_code, ExitCode
from fixtures import data_config


def test_successful(data_config):
    config = copy(data_config)
    config.scrum_path = "test/data/collection1"
    assert get_exit_code(config) == ExitCode.SUCCESSFUL


def test_invalid(data_config):
    config = copy(data_config)
    config.scrum_path = "test/fail_cases/invalid"
    assert get_exit_code(config) == ExitCode.INVALID_FILE


def test_rule_violation(data_config):
    config = copy(data_config)
    config.scrum_path = "test/fail_cases/rule_violation"
    assert get_exit_code(config) == ExitCode.RULE_VIOLATION
