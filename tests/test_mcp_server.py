def test_mcp_server_imports():
    from app.expense_tracker.mcp_server import mcp

    assert mcp.name == "PriceGenius Expense Tracker"
