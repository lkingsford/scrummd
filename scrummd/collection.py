import os
import pathlib
from typing import Optional
import scrummd.card
import logging
from scrummd.config import ScrumConfig

logger = logging.getLogger(__name__)


class DuplicateIndexError(ValueError):
    """Called when an index of a card is declared twice in the collection."""

    def __init__(self, index, path):
        self.index = index
        self.path = path
        super().__init__(f"Duplicate index {self.index} found in {self.path}")


def get_collection(
    config: ScrumConfig, collection_name: Optional[str] = None
) -> dict[str, scrummd.card.Card]:
    """Get a collection of cards

    Args:
        config (ScrumConfig): ScrumMD Configuration to use
        collection_name (Optional[str], optional): Collection to return. Defaults to None (being All).

    Raises:
        DuplicateIndexError: A card with an index is found twice

    Returns:
        dict[str, scrummd.card.Card]: A dict with the index of the card, and a card object
    """

    collection: dict[str, scrummd.card.Card] = {}
    collection_path = pathlib.Path(config.scrum_path)
    for root, _, files in os.walk(collection_path, followlinks=True):
        # So - this'll turn "scrum/backlog/special" into "backlog.special"
        collection_from_path = ".".join(
            pathlib.Path(root).relative_to(collection_path).parts
        )

        for name in files:
            path = pathlib.Path(root, name)
            if name[0] == ".":
                # Ignore all files that start with .
                continue
            try:
                with open(path, "r") as fo:
                    contents = fo.read()
                    card = scrummd.card.fromStr(
                        config, contents, [collection_from_path]
                    )
                    index = card["index"] or path.name.split(".")[0]
                    if index in collection:
                        raise DuplicateIndexError(index, path)
                    if not collection_name:
                        collection[index] = card
                    else:
                        for _collection in card["_collections"]:
                            if (
                                _collection == collection_name
                                or _collection.startswith(collection_name + ".")
                            ):
                                collection[index] = card

            except scrummd.card.ValidationError as ex:
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
