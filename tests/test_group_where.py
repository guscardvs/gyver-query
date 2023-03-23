import pytest
import sqlalchemy as sa
from gyver.database import make_table

from gyver.query.group import GroupWhere, and_, or_
from gyver.query.utils import compile_stmt
from gyver.query.where import Where

test_table = make_table(
    "test",
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.Text),
    sa.Column("age", sa.Integer),
)


@pytest.fixture
def engine():
    engine = sa.create_engine("sqlite:///:memory:", poolclass=sa.pool.StaticPool)
    with engine.connect() as conn:
        test_table.create(conn)
        conn.execute(
            test_table.insert().values(
                [
                    {"name": "Alice", "age": 25},
                    {"name": "Bob", "age": 30},
                    {"name": "Charlie", "age": 35},
                ]
            )
        )
        conn.commit()
    yield engine
    engine.dispose()


def test_group_where(engine: sa.Engine):
    with engine.connect() as conn:
        # Test that a GroupWhere with a single condition works
        gw = GroupWhere(
            Where("name", "Alice"),
            operator=sa.and_,
        )
        bound_gw = gw.bind(test_table)
        assert compile_stmt(bound_gw) == compile_stmt(
            sa.and_(test_table.c.name == "Alice")
        )
        result = conn.execute(sa.select(test_table).where(bound_gw)).mappings().all()
        assert len(result) == 1
        assert result[0]["name"] == "Alice"

        # Test that a GroupWhere with multiple conditions and "and" operator works
        gw = GroupWhere(
            Where("name", "Alice"),
            Where("age", 25),
            operator=sa.and_,
        )
        bound_gw = gw.bind(test_table)
        assert compile_stmt(bound_gw) == compile_stmt(
            sa.and_(test_table.c.name == "Alice", test_table.c.age == 25)
        )
        result = conn.execute(sa.select(test_table).where(bound_gw)).mappings().all()
        assert len(result) == 1
        assert result[0]["name"] == "Alice"

        # Test that a GroupWhere with multiple conditions and "or" operator works
        gw = GroupWhere(
            Where("name", "Alice"),
            Where("age", 30),
            operator=sa.or_,
        )
        bound_gw = gw.bind(test_table)
        assert compile_stmt(bound_gw) == compile_stmt(
            sa.or_(test_table.c.name == "Alice", test_table.c.age == 30)
        )
        result = conn.execute(sa.select(test_table).where(bound_gw)).mappings().all()
        assert len(result) == 2


def test_and_or(engine: sa.Engine):
    with engine.connect() as conn:
        # Test that an "and" condition works
        condition = and_(Where("name", "Alice"), Where("age", 25))
        bound_condition = condition.bind(test_table)
        assert compile_stmt(bound_condition) == compile_stmt(
            sa.and_(test_table.c.name == "Alice", test_table.c.age == 25)
        )
        result = (
            conn.execute(sa.select(test_table).where(bound_condition)).mappings().all()
        )
        assert len(result) == 1
        assert result[0]["name"] == "Alice"

        # Test that an "or" condition works
        condition = or_(Where("name", "Alice"), Where("age", 30))
        bound_condition = condition.bind(test_table)
        assert compile_stmt(bound_condition) == compile_stmt(
            sa.or_(test_table.c.name == "Alice", test_table.c.age == 30)
        )
        result = (
            conn.execute(sa.select(test_table).where(bound_condition)).mappings().all()
        )
