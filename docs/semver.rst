ScrumMD Versioning
==================

We are following `Semantic Versioning <https://semver.org/>`_.

We are implementing it in the following ways:

- There is no expectation of maintaining compatibility pre v1.0. Wild West zone.
- Until it's stable and announced, any changes to the output of the command line utilities (except ``svalid``) **are not regarded as a breaking change**. Scripts should rely on the Python libraries rather than calling the command line tools.
- Additional fields (and equivalents) provided are not a breaking change even if they change the order of the fields outputted. 