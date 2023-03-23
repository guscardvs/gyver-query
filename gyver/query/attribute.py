from functools import wraps
from typing import Callable, Hashable, Mapping, Optional, OrderedDict, cast

from gyver.attrs import call_init, define
from gyver.database.entity import AbstractEntity
from sqlalchemy.sql import ColumnElement
from typing_extensions import TypeGuard

from .exc import FieldNotFound
from .interface import FieldType, Mapper

CACHE_SIZE = 250


@define
class MaybeCache:
    _cache: OrderedDict[tuple[Mapper, str], FieldType]

    def __init__(self) -> None:
        call_init(self, OrderedDict())

    @property
    def cache(self) -> Mapping[tuple[Mapper, str], FieldType]:
        return self._cache

    def get(self, key: tuple[Mapper, str]) -> Optional[FieldType]:
        if not all(isinstance(item, Hashable) for item in key):
            return None
        if key in self._cache:
            value = self._cache.pop(key)
            self._cache[key] = value
            return value
        return None

    def put(self, key: tuple[Mapper, str], field: FieldType) -> FieldType:
        if not all(isinstance(item, Hashable) for item in key):
            return field
        if len(self._cache) >= CACHE_SIZE:
            self._cache.popitem(last=False)
        self._cache[key] = field
        return field

    def __call__(
        self, func: Callable[[Mapper, str], FieldType]
    ) -> Callable[[Mapper, str], FieldType]:
        @wraps(func)
        def inner(entity: Mapper, field: str) -> FieldType:
            if (attr := attr_cache.get((entity, field))) is not None:
                return attr
            return self.put((entity, field), func(entity, field))

        return inner


attr_cache = MaybeCache()


@attr_cache
def retrieve_attr(entity: Mapper, field: str) -> FieldType:
    is_entity = _is_entity(entity)
    if field == "id" and is_entity:
        field = "id_"
    if "." in field:
        if is_entity:
            return _retrieve_related_field(entity, field)
        raise FieldNotFound("query", field)
    try:
        return getattr(entity, field) if is_entity else getattr(entity.c, field)  # type: ignore
    except AttributeError:
        name = entity.__name__ if is_entity else "query"
        raise FieldNotFound(name, field) from None


def _is_entity(entity: Mapper) -> TypeGuard[type[AbstractEntity]]:
    return isinstance(entity, type) and issubclass(entity, AbstractEntity)


def _retrieve_related_field(entity: type[AbstractEntity], field: str) -> FieldType:
    *fields, target_field = field.split(".")
    current_mapper = entity
    for f in fields:
        if f == "id":
            f = "id_"
        try:
            attr = cast(ColumnElement, getattr(current_mapper, f))
        except AttributeError:
            raise FieldNotFound(entity.__name__, f) from None
        else:
            current_mapper = attr.entity.class_
    if target_field == "id":
        target_field = "id_"
    try:
        return getattr(current_mapper, target_field)
    except AttributeError:
        raise FieldNotFound(entity.__name__, field) from None
