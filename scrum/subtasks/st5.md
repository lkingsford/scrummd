---
Summary: Add option to force not using cache
Status: Ready
---

# Description

When `sbl`, `scard` or `sboard` perform any operations, `--no-cache` should
force the cache to not be used.

It should also rebuild the cache.

The option `disable_cache` should also be added to `tool.scrummd` in the config
file.
