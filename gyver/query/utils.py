import typing

import sqlalchemy as sa
from sqlalchemy.sql.elements import CompilerElement

from . import interface

T = typing.TypeVar("T")


def _make_converter(
    converter: typing.Callable[[interface.FieldType], interface.FieldType],
):
    def _converter(
        comparator: interface.Comparator[T],
    ) -> interface.Comparator[T]:
        def _comp(field: interface.FieldType, target: T) -> interface.SaComparison:
            return comparator(converter(field), target)

        return _comp

    return _converter


as_date = _make_converter(sa.func.date)
as_time = _make_converter(sa.func.time)
as_lower = _make_converter(sa.func.lower)
as_upper = _make_converter(sa.func.upper)


def compile_stmt(stmt: CompilerElement) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": True}))


__all__ = ["as_date", "as_time", "as_lower", "as_upper", "compile_stmt"]
