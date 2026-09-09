"""Separate MCP client for the private Cred support tool server."""

import asyncio
import sys

from fastmcp import Client


async def lookup(record_id: str) -> object:
    """Call the remote MCP tool through its HTTP transport."""
    async with Client("http://127.0.0.1:8001/mcp") as client:
        return await client.call_tool("lookup_loan_application", {"record_id": record_id})


if __name__ == "__main__":
    record_ids = sys.argv[1:] or ["LA-0001", "LA-0002"]
    for record_id in record_ids:
        print(record_id, asyncio.run(lookup(record_id)))
