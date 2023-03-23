import sqlalchemy as sa
from gyver.query.order_by import OrderDirection, OrderBy
from gyver.query.utils import compile_stmt
from tests import mocks


def test_orderby_classmethods_return_expected_order_by():
    assert OrderBy.asc("field") == OrderBy("field", OrderDirection.ASC)
    assert OrderBy.desc("field") == OrderBy("field", OrderDirection.DESC)
    assert OrderBy.none() == OrderBy(None, OrderDirection.ASC)


def test_order_by_apply_applies_order_correctly():
    stmt = sa.select(mocks.Another)

    assert compile_stmt(OrderBy.asc("id").apply(stmt)) == compile_stmt(
        stmt.order_by(mocks.Another.id_.asc())
    )

    assert compile_stmt(OrderBy.desc("id").apply(stmt)) == compile_stmt(
        stmt.order_by(mocks.Another.id_.desc())
    )

    assert OrderBy.none().apply(stmt) is stmt
