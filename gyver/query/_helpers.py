import sqlalchemy as sa
from gyver.attrs import define


@define
class MockTable:
    c: sa.ColumnCollection
