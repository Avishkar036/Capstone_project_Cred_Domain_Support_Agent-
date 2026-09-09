"""Separate MCP client for the private Cred support tool server."""

import asyncio
import sys

from fastmcp import Client


async def lookup(record_id: str) -> object:
    """Call the remote MCP tool through its HTTP transport."""
    async with Client("http://127.0.0.1:8001/mcp") as client:
        return await client.call_tool("lookup_loan_application", {"record_id": record_id})


if __name__ == "__main__":
    record_id = sys.argv[1] if len(sys.argv) > 1 else "LA-0001"
    print(asyncio.run(lookup(record_id)))
