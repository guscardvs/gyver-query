import typing

import sqlalchemy as sa
from gyver.attrs import call_init, define

from . import attribute
from . import comp as cp
from . import interface
from .group import and_
from .typedef import ClauseType

T = typing.TypeVar("T")


@define
class Resolver(typing.Generic[T]):
    val: typing.Any

    def resolve(self, mapper: interface.Mapper) -> T:
        del mapper
        return self.val

    def __bool__(self):
        return self.val is not None


class FieldResolver(Resolver[str]):
    def resolve(self, mapper: interface.Mapper):
        return attribute.retrieve_attr(mapper, self.val)


@define(frozen=False)
class Where(interface.BindClause, typing.Generic[T]):
    field: str
    expected: Resolver[T]
    comp: interface.Comparator[T] = cp.equals

    def __init__(
        self,
        field: str,
        expected: typing.Optional[T] = None,
        comp: interface.Comparator[T] = cp.equals,
        resolver_class: type[Resolver[T]] = Resolver,
    ) -> None:
        call_init(
            self,
            field,
            resolver_class(expected),
            comp,
        )

    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.SaComparison:
        resolved = self.expected.resolve(mapper)
        attr = attribute.retrieve_attr(mapper, self.field)
        return self.comp(attr, resolved) if self.expected else sa.true()


_placeholder_column = sa.Column("placeholder")


class AlwaysTrue(interface.BindClause):
    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.SaComparison:
        return cp.always_true(_placeholder_column, mapper)


class RawQuery(interface.BindClause):
    type_ = ClauseType.BIND

    def __init__(self, cmp: interface.SaComparison) -> None:
        self._cmp = cmp

    def bind(self, mapper: interface.Mapper) -> interface.SaComparison:
        del mapper
        return self._cmp


class ApplyWhere(interface.ApplyClause):
    type_ = ClauseType.APPLY

    def __init__(self, mapper: interface.Mapper, *where: interface.BindClause) -> None:
        self.where = and_(*where).bind(mapper)

    def apply(self, query: interface.ExecutableT) -> interface.ExecutableT:
        return query.where(self.where)
