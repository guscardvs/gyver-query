import sqlalchemy as sa

from gyver.query.paginate import FieldPaginate, LimitOffsetPaginate, Paginate
from gyver.query.utils import compile_stmt
from tests import mocks


def test_null_paginate_does_not_change_the_query():
    stmt = sa.select(mocks.Another)
    assert Paginate.none().apply(stmt) is stmt


def test_limit_offset_paginate_applies_pagination_in_query():
    stmt = sa.select(mocks.Another)
    limit, offset = 10, 5
    assert compile_stmt(LimitOffsetPaginate(limit, offset).apply(stmt)) == compile_stmt(
        stmt.limit(limit).offset(offset)
    )


def test_field_paginate_applies_field_pagination_in_query():
    stmt = sa.select(mocks.Another)
    limit, offset = 10, 5
    assert compile_stmt(FieldPaginate(limit, offset).apply(stmt)) == compile_stmt(
        stmt.where(mocks.Another.id_ > offset).limit(limit)
    )


def test_field_paginate_applies_field_pagination_to_different_fields():
    stmt = sa.select(mocks.PersonAddress)
    limit, offset = 10, 5
    assert compile_stmt(
        FieldPaginate(limit, offset, "another_id").apply(stmt)
    ) == compile_stmt(stmt.where(mocks.PersonAddress.another_id > offset).limit(limit))


def test_field_paginate_applies_field_pagination_to_the_expected_column():
    stmt = sa.select(mocks.PersonAddress, mocks.Another)
    limit, offset = 10, 5
    assert compile_stmt(FieldPaginate(limit, offset).apply(stmt)) == compile_stmt(
        stmt.where(mocks.PersonAddress.id_ > offset).limit(limit)
    )


def test_field_paginate_gets_correct_field_on_join():
    stmt = sa.select(mocks.PersonAddress).outerjoin(mocks.Another)
    limit, offset = 10, 5
    assert compile_stmt(FieldPaginate(limit, offset).apply(stmt)) == compile_stmt(
        stmt.where(mocks.PersonAddress.id_ > offset).limit(limit)
    )
