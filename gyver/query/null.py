import sqlalchemy as sa

from .typedef import ClauseType

from . import interface


class NullBind(interface.BindClause):
    type_ = ClauseType.BIND

    def bind(self, mapper: interface.Mapper) -> interface.SaComparison:
        del mapper
        return sa.true()
