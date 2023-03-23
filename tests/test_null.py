import sqlalchemy as sa

from gyver.query.null import NullBind
from gyver.query.utils import compile_stmt
from tests import mocks


def test_null_bind_always_returns_sa_true_on_bind():
    assert compile_stmt(NullBind().bind(mocks.Another)) == compile_stmt(sa.true())
