from functools import wraps
import typing
from datetime import date
from datetime import time
import typing_extensions

import sqlalchemy as sa
from sqlalchemy.sql import Delete
from sqlalchemy.sql import Select
from sqlalchemy.sql import Update
from sqlalchemy.sql.elements import BooleanClauseList
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.functions import Function

from gyver.database.entity import AbstractEntity
from .typedef import ClauseType

P = typing_extensions.ParamSpec("P")

ExecutableType = typing.Union[Select, Update, Delete]
ExecutableT = typing.TypeVar("ExecutableT", bound=ExecutableType)
Sortable = typing.Union[int, float, date, time]
Comparison = typing.Union[
    ColumnElement[sa.Boolean], BooleanClauseList, Function
]
SaComparison = ColumnElement[bool]
FieldType = typing.Union[ColumnElement, sa.Column]
T = typing.TypeVar("T", contravariant=True)
Mapper = typing.Union[sa.Table, type[AbstractEntity]]


def cast_comp(comp: Comparison) -> SaComparison:
    return typing.cast(typing.Any, comp)


def as_comp(
    func: typing.Callable[P, Comparison]
) -> typing.Callable[P, SaComparison]:
    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> SaComparison:
        return cast_comp(func(*args, **kwargs))

    return inner


class Comparator(typing.Protocol[T]):
    def __call__(self, field: FieldType, target: T) -> SaComparison:
        ...


class Clause(typing.Protocol):
    type_: typing.ClassVar[ClauseType]


class BindClause(Clause, typing.Protocol):
    type_: typing.Literal[ClauseType.BIND]

    def bind(self, mapper: Mapper) -> SaComparison:
        ...


class ApplyClause(Clause, typing.Protocol[ExecutableT]):
    type_: typing.Literal[ClauseType.APPLY]

    def apply(self, query: ExecutableT) -> ExecutableT:
        ...
