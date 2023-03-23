import pytest

from gyver.query.attribute import retrieve_attr
from gyver.query.exc import FieldNotFound
from .mocks import Another, PersonAddress, mock_table


def test_retrieve_attr_gets_attribute_from_entity():
    assert retrieve_attr(Another, "name") == Another.name


def test_retrieve_attr_gets_attribute_from_column():
    assert retrieve_attr(mock_table, "id") == mock_table.c.id


def test_retrieve_attr_gets_attribute_from_related_entity():
    assert retrieve_attr(PersonAddress, "another.name") == Another.name


def test_retrieve_attr_raises_FieldNotFound_for_nonexistent_attribute():
    with pytest.raises(FieldNotFound):
        retrieve_attr(Another, "nonexistent_attr")


def test_retrieve_attr_raises_FieldNotFound_for_nonexistent_related_attribute():
    with pytest.raises(FieldNotFound):
        retrieve_attr(PersonAddress, "nonexistent_attr.person.name")
