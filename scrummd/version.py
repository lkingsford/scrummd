import sys

try:
    from . import _version

    version = _version.version
except ImportError:
    version = "dev"


def version_to_output() -> str:
    """Return the version of python and the version of scrummd to output to the user.

    Returns:
        str: String suitable for stdout --version output
    """
    return f"ScrumMD: v{version}. Python: {sys.version}"
