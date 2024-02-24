## ScrumMD

**ScrumMD** is a phenomenally bad idea made into an experiment. With no specific plan as to whether that experiment will be finished. Here's what it is:

What if we could have a scrum board driven entirely by md files and the CLI, and use it with git?

## License

This is published under the [GNU General Public License v3.0](LICENSE.md). I am willing to discuss making it available under another license, or providing paid support.

## Usage

### Collection

A basic collection is a folder on the file system, grouped and containing cards.

All cards and collections are by default in the `scrum` folder. Any folders containing cards within the `scrum` folder are collections.

### Card

A card consists of fields in two formats:

```
---
key: value
key2: value
---
```

and

```
# Key

Multiline value
```

See [scrum/backlog] for examples.

A card's index (card number) is its file name. All cards **must** have a summary.

### `sbl`

```
usage: sbl [-h] [-c [COLUMNS]] [-b] [-o] [collection]

Display a collection of scrum cards

positional arguments:
  collection            The collection to return. If none is given, all cards are returned.

options:
  -h, --help            show this help message and exit
  -c [COLUMNS], --columns [COLUMNS]
                        A comma separated list of columns to return.
  -b, --bare            Return bare paths only suitable for scripting. Effectively shorthand for `sbl -o -c _path`.
  -o, --omit-headers    Omit headers from output.
```

### `scard`

```
usage: scard [-h] [card ...]

positional arguments:
  card        Index of cards to return

options:
  -h, --help  show this help message and exit
```

### Fields

The following special fields are available:

| Field         | Required | Description                                 |
| ------------- | -------- | ------------------------------------------- |
| `summary`     | Y        | A title of the card shown in most outputs   |
| `index`       | N        | Replace the filename with a new card number |
| `tags`        | N        | Additional collections to put the card in   |
| `collections` | N        | Synonym for `tags`                          |
| `items`       | N        | Items if card index is used as a collection |
| `_path`       | RO       | The relative path of the card               |

The fields marked RO are Read Only and are set by scummd. They can be used (for instance) as columns with `sbl`.

### Advanced Collections

A card can also be added in collections by adding them to a `collections` or `tags` field.

In addition, any cards which contain card indexes in fields in the format of `[[index]]` will create a collection. If they're in a field called `items`, any cards listed will be in a collection with the same name as the index of the card. If they're in an other field, they'll create a collection in the format `index.fieldname`. So - for example:

```md
---
Summary: Test collection in field of card
Index: epic1
Key: [[c5]]
---

# Description

Additional text

# Items

-   [[c1]]
-   [[c2]]

# Special

-   [[c1]]
-   [[c4]]
```

will create a collection called `epic1` containing `c1`, `c2`, `c3`, `c4` and `c5` (as collections are included in their parent). It will also create a collection called `epic1.special` containing `c1` and `c4`, and a collection called `epic1.key` containing `c5`.

This can be used to create groups of cards for things like sprints, epics or tracing relationships (such as dependencies) between cards.

### Configuration

Configuration can be stored in the priority order of:

-   `.scrum.toml`
-   `scrum.toml`
-   `pyproject.taml`.
-   In all cases, under the `[tools.scrummd]` table.

Initial settings that are supported are

| Setting      | type         | Description                                                           |
| ------------ | ------------ | --------------------------------------------------------------------- |
| strict       | bool         | Fail on any issue with the collection rather than trying to persevere |
| scrum_path   | str          | Path of the scrum cards/meta                                          |
| columns      | array of str | Array of columns to show with `sbl`                                   |
| omit_headers | bool         | Hide headers from `sbl` output                                        |
| fields       | table        | Limit fields to specific values. Each member is an array of str.      |

#### Example Config

```toml
[tool.scrummd]
strict = true
scrum_path = "scrum"
columns = ["index", "status", "summary"]
omit_headers = false

[tool.scrummd.fields]
status = ["Not Fully Defined", "Ready", "In Progress", "In Testing", "Done"]
```
