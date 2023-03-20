from gyver.query import comp
from gyver.query.utils import compile_stmt
from gyver.query.where import Where
import sqlalchemy as sa
from .mocks import Person


def test_sa_select_builds_correctly():
    assert compile_stmt(
        sa.select(Person).where(Person.id_ > 1)
    ) == compile_stmt(
        sa.select(Person).where(Where("id", 1, comp.greater).bind(Person))
    )
