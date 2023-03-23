import sqlalchemy as sa

from . import interface
from .typedef import ClauseType


class NullBind(interface.BindClause):
    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.SaComparison:
        del mapper
        return sa.true()
