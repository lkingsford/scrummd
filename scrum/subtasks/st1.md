---
Summary: Create paths/changes db
Status: Ready
---

# Description

Create a cache file in the scrum folder - default to `.scrumcache` but allow
`cache_file` in `tools.scrummd` in the config.

Populate it with the paths, indexes and the most recent file change/created
time on each command.

Update any files that have changed only.