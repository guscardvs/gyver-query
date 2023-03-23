import warnings
from typing import Callable, Optional, Sequence

import sqlalchemy as sa
from gyver.attrs import call_init, define

from . import interface


@define
class GroupWhere:
    where: Sequence[interface.BindClause]
    operator: Callable[..., interface.SaComparison]
    mark: Optional[str]

    def __init__(
        self,
        *where: interface.BindClause,
        operator: Callable[..., interface.SaComparison],
        mark: Optional[str] = None,
        strict: bool = True,
    ) -> None:
        if not where:
            raise ValueError("GroupWhere requires at least one item")
        marked = [item for item in where if getattr(item, "mark", None) in (None, mark)]
        if len(marked) != len(where) and strict and mark is not None:
            warnings.warn(
                "GroupWhere with flag strict received clauses with different mark"
            )
        call_init(self, tuple(marked), operator, mark)

    def __bool__(self):
        return bool(self.where)

    def bind(self, mapper: interface.Mapper) -> interface.SaComparison:
        return self.operator(*(clause.bind(mapper) for clause in self.where))


def and_(
    *where: interface.BindClause,
    mark: Optional[str] = None,
    strict: bool = True,
) -> GroupWhere:
    return GroupWhere(*where, operator=sa.and_, mark=mark, strict=strict)


def or_(
    *where: interface.BindClause,
    mark: Optional[str] = None,
    strict: bool = True,
) -> GroupWhere:
    return GroupWhere(*where, operator=sa.or_, mark=mark, strict=strict)
