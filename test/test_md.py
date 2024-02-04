import os
import pytest
import scrumcli.md as md


@pytest.fixture(scope="function")
def md1_fo() -> str:
    fo = open("test/data/md1.md")
    yield fo
    fo.close()


def test_basic_extract(md1_fo):
    """Test extracting both property and header style variables from an md file"""
    results = md.extract_fields(md1_fo)
    assert results["summary"] == "Summary of card"
    assert results["status"] == "Status of card"
    assert (
        results["description"].strip()
        == """Multi line description

here"""
    )
