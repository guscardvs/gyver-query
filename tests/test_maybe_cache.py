from sqlalchemy import Column, Integer, MetaData, String, Table

from gyver.query.attribute import CACHE_SIZE, MaybeCache
from gyver.query.interface import Mapper


def test_get_returns_cached_value():
    cache = MaybeCache()
    metadata = MetaData()
    table = Table("my_table", metadata, Column("id", Integer), Column("name", String))
    cache.put((table, "id"), table.c.id)
    assert cache.get((table, "id")) == table.c.id


def test_get_returns_none_for_non_hashable_key():
    cache = MaybeCache()
    metadata = MetaData()
    table = Table("my_table", metadata, Column("id", Integer), Column("name", String))
    assert cache.get((table, ["non-hashable"])) is None  # type: ignore


def test_put_adds_to_cache():
    cache = MaybeCache()
    metadata = MetaData()
    table = Table("my_table", metadata, Column("id", Integer), Column("name", String))
    cache.put((table, "id"), table.c.id)
    assert cache.cache[(table, "id")] == table.c.id


def test_put_overwrites_existing_cache_value():
    cache = MaybeCache()
    metadata = MetaData()
    table = Table("my_table", metadata, Column("id", Integer), Column("name", String))
    cache.put((table, "id"), table.c.id)
    cache.put((table, "id"), table.c.name)
    assert cache.cache[(table, "id")] == table.c.name


def test_put_removes_oldest_cache_value_when_cache_size_is_reached():
    cache = MaybeCache()
    metadata = MetaData()
    table = Table("my_table", metadata, Column("id", Integer), Column("name", String))
    for i in range(CACHE_SIZE):
        cache.put((table, f"field{i}"), table.c.id)
    cache.put((table, "new_field"), table.c.name)
    assert cache.cache.get((table, "field0")) is None


def test_decorator_caches_function_result():
    cache = MaybeCache()
    metadata = MetaData()
    table = Table("my_table", metadata, Column("id", Integer), Column("name", String))

    @cache
    def get_field(mapper: Mapper, field: str):
        return getattr(mapper.c, field)  # type: ignore

    get_field(table, "name")

    assert cache.cache[(table, "name")] == table.c.name
