"""MCP connector for Lean."""

from scion_sdk.connector import Connector

from .api_client import Api
from .auth import get_client

connector = Connector(
    api=Api,
    get_client=get_client,
    instructions="Operate Lean. Read before you change; confirm before you delete.",
)
