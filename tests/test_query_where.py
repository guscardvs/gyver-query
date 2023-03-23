import sqlalchemy as sa
from gyver.database import default_metadata

from gyver.query import comp
from gyver.query.utils import compile_stmt
from gyver.query.where import (
    AlwaysTrue,
    ApplyWhere,
    FieldResolver,
    RawQuery,
    Resolver,
    Where,
)

from .mocks import Entity

mapper = sa.Table(
    "users",
    default_metadata,
    sa.Column("id", sa.Integer),
    sa.Column("name", sa.String),
)


class TableMock(Entity):
    pass


def test_resolve_with_other_type():
    resolver = Resolver[int](5)
    assert resolver.resolve(mapper) == 5


def test_bool_with_none():
    resolver = Resolver[int](None)
    assert not resolver


def test_bool_with_non_none():
    resolver = Resolver[int](5)
    assert bool(resolver)


def test_resolve():
    resolver = FieldResolver("id")
    assert resolver.resolve(mapper) == mapper.c.id


def test_bind_with_always_true_comp():
    where = Where("id", 5, comp.always_true)
    assert where.bind(mapper) == AlwaysTrue().bind(mapper)


def test_where_bind_returns_valid_comparison():
    where = Where("id", 5)
    assert compile_stmt(where.bind(mapper)) == compile_stmt(mapper.c.id == 5)


def test_where_runs_correctly_other_comp():
    where = Where("id", 5, comp.greater)
    assert compile_stmt(where.bind(mapper)) == compile_stmt(mapper.c.id > 5)


def test_raw_query_returns_same_value_received():
    q = mapper.c.id > 5

    assert RawQuery(q).bind(mapper) is q


def test_apply_where_returns_the_expected_result():
    initial = sa.select(mapper)

    assert compile_stmt(
        ApplyWhere(mapper, Where("id", 5, comp.greater)).apply(initial)
    ) == compile_stmt(initial.where(mapper.c.id > 5))
