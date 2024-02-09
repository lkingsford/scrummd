import os
import pathlib
import scrumcli.card
import logging
from scrumcli.config import ScrumConfig

logger = logging.getLogger(__name__)


class DuplicateIndexError(ValueError):
    """Called when an index of a card is declared twice in the collection."""

    def __init__(self, index, path):
        self.index = index
        self.path = path
        super().__init__(f"Duplicate index {self.index} found in {self.path}")


def get_collection(
    config: ScrumConfig, collection_name: str
) -> dict[str, scrumcli.card.Card]:
    collection: dict[str, scrumcli.card.Card] = {}
    collection_path = pathlib.Path(config.scrum_path, *(collection_name.split(".")))
    for root, dirs, files in os.walk(collection_path, followlinks=True):
        for name in files:
            path = pathlib.Path(root, name)
            if name[0] == ".":
                # Ignore all files that start with .
                continue
            try:
                with open(path, "r") as fo:
                    contents = fo.read()
                    card = scrumcli.card.fromStr(config, contents)
                    index = card["index"] or path.name.split(".")[0]
                    if index in collection:
                        raise DuplicateIndexError(index, path)
                    collection[index] = card

            except scrumcli.card.ValidationError as ex:
                if config.strict:
                    raise
                else:
                    logging.warn("ValidationError (%s) reading %s", ex, path)

            except DuplicateIndexError as ex:
                if config.strict:
                    raise
                else:
                    logging.warn("%s ignored", path)

    return collection
