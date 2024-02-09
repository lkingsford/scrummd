## ScrumMD

**ScrumMD** is a phenomenally bad idea made into an experiment. With no specific plan as to whether that experiment will be finished. Here's what it is:

What if we could have a scrum board driven entirely by md files and the CLI, and use it with git?

## License

This is published under the [GNU General Public License v3.0](LICENSE.md). I am willing to discuss making it available under another license, or providing paid support.

## Usage

### Basic collection

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
usage: sbl [-h] [collection]

Display a collection of scrum cards

positional arguments:
  collection  The collection to return. If none is given, all cards are returned.

options:
  -h, --help  show this help message and exit
```

### `scard`

```
usage: scard [-h] [card ...]

positional arguments:
  card        Index of cards to return

options:
  -h, --help  show this help message and exit
```

### Configuaration

Configuration can be stored in the priority order of:

-   `.scrum.toml`
-   `scrum.toml`
-   `pyproject.taml`.
-   In all cases, under the `[tools.scrummd]` heading.

Initial settings that are supported are

| Setting    | Description                                                           |
| ---------- | --------------------------------------------------------------------- |
| strict     | Fail on any issue with the collection rather than trying to persevere |
| scrum_path | Path of the scrum cards/meta                                          |
