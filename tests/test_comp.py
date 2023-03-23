from datetime import datetime

import sqlalchemy as sa

from gyver.query import comp, where
from gyver.query.utils import as_date, as_time, compile_stmt

from .mocks import Another, Person, PersonAddress


def test_comparison_matches_expected():  # sourcery skip: none-compare
    assert comp.always_true(Person.name, object()) == sa.true()
    assert compile_stmt(comp.equals(Person.name, "test")) == compile_stmt(
        Person.name == "test"
    )
    assert compile_stmt(comp.not_equals(Person.name, "test")) == compile_stmt(
        Person.name != "test"
    )
    assert compile_stmt(comp.greater(Person.age, 46)) == compile_stmt(Person.age > 46)
    assert compile_stmt(comp.greater_equals(Person.age, 46)) == compile_stmt(
        Person.age >= 46
    )
    assert compile_stmt(comp.lesser(Person.age, 46)) == compile_stmt(Person.age < 46)
    assert compile_stmt(comp.lesser_equals(Person.age, 46)) == compile_stmt(
        Person.age <= 46
    )
    assert compile_stmt(comp.between(Person.age, (45, 52))) == compile_stmt(
        Person.age.between(45, 52)
    )
    assert compile_stmt(comp.range(Person.age, (45, 52))) == compile_stmt(
        sa.and_(Person.age >= 45, Person.age < 52)
    )
    assert compile_stmt(comp.like(Person.name, "test")) == compile_stmt(
        Person.name.like("%test%")
    )
    assert compile_stmt(comp.rlike(Person.name, "test")) == compile_stmt(
        Person.name.like("test%")
    )
    assert compile_stmt(comp.llike(Person.name, "test")) == compile_stmt(
        Person.name.like("%test")
    )
    assert compile_stmt(comp.insensitive_like()(Person.name, "test")) == compile_stmt(
        Person.name.ilike("%test%")
    )
    assert compile_stmt(
        comp.insensitive_like("llike")(Person.name, "test")
    ) == compile_stmt(Person.name.ilike("test%"))
    assert compile_stmt(
        comp.insensitive_like("rlike")(Person.name, "test")
    ) == compile_stmt(Person.name.ilike("%test"))
    assert compile_stmt(comp.isnull(Person.name, True)) == compile_stmt(
        Person.name.is_(None)
    )
    assert compile_stmt(comp.isnull(Person.name, False)) == compile_stmt(
        Person.name.is_not(None)
    )
    now = datetime.now()
    assert compile_stmt(
        as_date(comp.equals)(Person.last_login, now.date())
    ) == compile_stmt(sa.func.date(Person.last_login) == now.date())
    assert compile_stmt(
        as_time(comp.greater)(Person.last_login, now.time())
        == compile_stmt(sa.func.time(Person.last_login) > now.time())
    )


def test_field_resolver_resolves_correctly():
    assert compile_stmt(
        where.Where(
            "another.id", "another_id", resolver_class=where.FieldResolver
        ).bind(PersonAddress)
    ) == compile_stmt(Another.id_ == PersonAddress.another_id)
