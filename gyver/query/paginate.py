from abc import ABC, abstractmethod

from gyver.attrs import define
from sqlalchemy.sql import Select

from . import comp as cp
from ._helpers import MockTable
from .interface import ApplyClause, Comparator
from .typedef import ClauseType
from .where import Where


@define
class Paginate(ApplyClause, ABC):
    type_ = ClauseType.APPLY
    limit: int
    offset: int

    @abstractmethod
    def apply(self, query: Select) -> Select:
        raise NotImplementedError

    @staticmethod
    def none():
        return _NullPaginate(limit=0, offset=0)

    def __bool__(self):
        return isinstance(self, _NullPaginate)


class LimitOffsetPaginate(Paginate):
    def apply(self, query: Select) -> Select:
        return query.limit(self.limit).offset(self.offset)


@define
class FieldPaginate(Paginate):
    field: str = "id"
    jump_comparison: Comparator[int] = cp.greater

    def apply(self, query: Select) -> Select:
        return query.where(
            Where(self.field, self.offset, self.jump_comparison).bind(
                MockTable(query.selected_columns)
            )
        ).limit(self.limit)


class _NullPaginate(Paginate):
    def apply(self, query: Select) -> Select:
        return query
