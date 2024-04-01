"""Generate a collection, and time accessing it for benchmarking common scrummd functions."""

import argparse
from pathlib import Path
from statistics import mean
import timeit
import logging
import tempfile
import contextlib
from collections.abc import Iterator
import random
from scrummd.collection import SortCriteria, get_collection, sort_collection
from scrummd.version import version_to_output
from scrummd.config import ScrumConfig


def rand_str(size: int, whitespace: bool = False):
    return "".join(
        [
            random.choice(
                f"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ{' ' if whitespace else ''}"
            )
            for _ in range(size)
        ]
    )


@contextlib.contextmanager
def scrum_repo(
    count: int, references: int, minsize: int, sortcount: int
) -> Iterator[ScrumConfig]:
    """Create a temporary folder full of cards

    Args:
        count (int): Amount of files to generate
        references (int): Amount of card references to add to each card
        minsize (int): Min size of each card in bytes
        sortcount (int): Amount of sort criteria to apply

    Returns:
        ScrumConfig: The ScrumConfig to load files with
    """
    logging.info("Creating scrum repo")
    with tempfile.TemporaryDirectory() as tmpdir:
        for cardno in range(count):
            path = Path(tmpdir, f"c{cardno}.md")
            with open(path, "w") as card_f:
                logging.debug("Writing %s", [path])
                cur_references: list[str] = []
                contents = f"---\n summary: {rand_str(50)}"
                for sortnum in range(sortcount):
                    contents += f"\ns{sortnum}: {random.choice([random.randint(0,20), rand_str(2)]) }"
                contents += "\n---"
                block_count = 0
                while len(contents) < minsize and len(cur_references) < references:
                    block_count += 1
                    block_type = random.choice(["str", "list"])
                    contents += f"\n\n#header{block_count} \n\n"
                    if block_type == "str":
                        while random.random() > 0.2:
                            contents += rand_str(10)
                            if random.random() < 0.3:
                                reference = f"c{random.choice(range(count))}"
                                cur_references.append(reference)
                                contents += f"[[{reference}]]"
                            if random.random() < 0.2:
                                contents += "\n"
                    if block_type == "list":
                        while random.random() > 0.2:
                            contents += "\n- "
                            if random.random() < 0.5:
                                contents += rand_str(50)
                            else:
                                reference = f"c{random.choice(range(count))}"
                                cur_references.append(reference)
                                contents += f"[[{reference}]]"
                card_f.write(contents)

        yield ScrumConfig(scrum_path=tmpdir)
    logging.info("Cleaned up")


def create_parser() -> argparse.ArgumentParser:
    """Return argument parser for sbench

    Returns:
        ArgumentParser: Parser for sbench
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--count", help="Count of files to attempt collection with", default=10000
    )
    parser.add_argument(
        "--references", help="Amount of references to add in each card", default=10
    )
    parser.add_argument(
        "--size", help="Minimum size of each card in bytes", default=1000
    )
    parser.add_argument("--times", help="Times to test collection", default=5)
    parser.add_argument("--sorts", help="Amount of sort criteria to sort by", default=2)
    # parser.add_argument(
    #    "--cache", help="Test twice each time to test caching time", action="store_true"
    # )
    parser.add_argument("-v", help="Level of verbosity", action="count", default=0)
    parser.add_argument(
        "--version",
        action="version",
        version=version_to_output(),
    )
    parser.description == __doc__

    return parser


def entry():
    """Entry point for sbench"""

    args = create_parser().parse_args()

    logging.basicConfig(level=30 - args.v * 10)

    with scrum_repo(
        int(args.count), int(args.references), int(args.size), int(args.sorts)
    ) as config:
        times = []
        print(f"get_collection executions")
        for count in range(int(args.times)):
            ex_time = timeit.timeit(lambda: get_collection(config), number=1)
            times.append(ex_time)
            print(f"{count}: {ex_time} s")
        print(f" Avg: {mean(times)} s")

        if args.sorts > 0:
            sort_times = []
            collection = get_collection(config)
            print("\nsort_collection executions")
            criteria = [
                SortCriteria(f"s{sort_number}", False)
                for sort_number in range(args.sorts)
            ]
            for count in range(int(args.times)):
                ex_time = timeit.timeit(
                    lambda: sort_collection(collection, criteria), number=1
                )
                sort_times.append(ex_time)
                print(f"{count}: {ex_time} s")
            print(f" Avg: {mean(sort_times)} s")


if __name__ == "__main__":
    entry()
