"""Return an exit code if there's any invalid files, or rules being broken.

Returns: 0 if Successful; 1 if Exception Raised; 2 if Invalid File; 3 if Rules Violation.

"""

import argparse
from enum import Enum
import sys

from scrummd.collection import get_collection
from scrummd.config import ScrumConfig
from scrummd.config_loader import load_fs_config
from scrummd.exceptions import InvalidFileError, RuleViolationError


class ExitCode(Enum):
    SUCCESSFUL = 0
    OTHER_FAILURE = 1
    INVALID_FILE = 2
    RULE_VIOLATION = 3


def get_exit_code(config: ScrumConfig) -> ExitCode:
    """Return what the exit code should be

    Returns:
        ExitCode: Validation status of the repository
    """

    config.strict = True

    try:
        get_collection(config)
    except InvalidFileError:
        return ExitCode.INVALID_FILE
    except RuleViolationError:
        return ExitCode.RULE_VIOLATION
    except Exception as e:
        raise e

    return ExitCode.SUCCESSFUL


def entry() -> None:
    parser = argparse.ArgumentParser()
    parser.description = __doc__
    parser.parse_args()

    config = load_fs_config()

    sys.exit(get_exit_code(config).value)


if __name__ == "__main__":
    entry()
