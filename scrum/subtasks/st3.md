---
Summary: Load cards into cache
Status: Ready
---

# Description

For each new or modified (dirty) scrum card, load it into the cache when making
any operation that reads the backlog.

The fields must be extracted into columns (for the default fields) and into
a UDF table.

Relationships and collections should also be loaded into tables.

Anything invalidating a card should wipe it from all effected tables.

# Depends On

-   [[st1]]
