"""The one place the Lean client is declared: a runner over the local toolchain."""

from .api_client import Api
from .runner import LeanRunner


def get_client() -> Api:
    """Return the client over the configured workspace root."""
    return Api(LeanRunner.from_env())
