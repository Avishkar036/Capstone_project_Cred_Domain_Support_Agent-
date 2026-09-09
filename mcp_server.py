"""Private FastMCP server exposing the loan-status tool."""

from fastmcp import FastMCP

from loan_tools import check_loan_application_status


mcp = FastMCP("Cred Support Tools")


@mcp.tool()
def lookup_loan_application(record_id: str) -> dict:
    """Look up a loan application's status, amount, and escalation score."""
    return check_loan_application_status(record_id)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001)
