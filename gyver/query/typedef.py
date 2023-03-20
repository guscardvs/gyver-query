from enum import Enum


class OrderDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"
    DISABLED = "disabled"


class ClauseType(str, Enum):
    BIND = "bind"
    APPLY = "apply"
