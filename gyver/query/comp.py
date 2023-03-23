import typing

import sqlalchemy as sa

from . import interface


def always_true(
    field: interface.FieldType, target: typing.Any
) -> interface.SaComparison:
    del field, target
    return sa.true()


def equals(field: interface.FieldType, target: typing.Any) -> interface.SaComparison:
    return field == target


def not_equals(
    field: interface.FieldType, target: typing.Any
) -> interface.SaComparison:
    return field != target


def greater(
    field: interface.FieldType, target: interface.Sortable
) -> interface.SaComparison:
    return field > target


def greater_equals(
    field: interface.FieldType, target: interface.Sortable
) -> interface.SaComparison:
    return field >= target


def lesser(
    field: interface.FieldType, target: interface.Sortable
) -> interface.SaComparison:
    return field < target


def lesser_equals(
    field: interface.FieldType, target: interface.Sortable
) -> interface.SaComparison:
    return field <= target


def between(
    field: interface.FieldType,
    target: tuple[interface.Sortable, interface.Sortable],
) -> interface.SaComparison:
    left, right = target
    return field.between(left, right)


def range(
    field: interface.FieldType,
    target: tuple[interface.Sortable, interface.Sortable],
) -> interface.SaComparison:
    left, right = target
    return sa.and_(greater_equals(field, left), (lesser(field, right)))


def like(field: interface.FieldType, target: str) -> interface.SaComparison:
    return field.like(f"%{target}%")


def rlike(field: interface.FieldType, target: str) -> interface.SaComparison:
    return field.like(f"{target}%")


def llike(field: interface.FieldType, target: str) -> interface.SaComparison:
    return field.like(f"%{target}")


def insensitive_like(
    opt: typing.Literal["like", "rlike", "llike"] = "like"
) -> interface.Comparator[str]:
    fmt = {"like": "%{target}%", "rlike": "%{target}", "llike": "{target}%"}[opt]

    def comparator(field: interface.FieldType, target: str):
        return field.ilike(fmt.format(target=target))

    return comparator


def isnull(field: interface.FieldType, target: bool) -> interface.SaComparison:
    return field.is_(None) if target else field.is_not(None)


def includes(
    field: interface.FieldType, target: typing.Sequence
) -> interface.SaComparison:
    return field.in_(list(target))


def excludes(
    field: interface.FieldType, target: typing.Sequence
) -> interface.SaComparison:
    return field.not_in(list(target))


def json_contains(
    field: interface.FieldType, target: typing.Any
) -> interface.SaComparison:
    return sa.func.json_contains(field, f'"{target}"')


def json_empty(
    field: interface.FieldType, target: typing.Any
) -> interface.SaComparison:
    func_length = sa.func.json_length(field)
    return func_length == 0 if target else func_length != 0


def make_relation_check(
    clause: interface.BindClause,
) -> interface.Comparator[bool]:
    def _relation_exists(
        field: interface.FieldType, target: bool
    ) -> interface.SaComparison:
        comp = clause.bind(field.class_)
        func = (
            field.has
            if field.property.direction.name.lower() not in ("onetomany", "manytomany")
            else field.any
        )
        result = func() if str(comp) == str(sa.true()) else func(comp)
        return result if target else ~result

    return _relation_exists
