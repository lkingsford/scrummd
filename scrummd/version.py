try:
    from . import _version

    version = _version.version
except ImportError:
    version = "dev"
