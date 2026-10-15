import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from statement_service import AccountStatement, InspectionReminder, MaintenanceRequest, TenantDocument, follow_up_required, statement_markdown


def test_pending_document_requires_follow_up_and_appears_in_statement():
    statement = AccountStatement("Ari", "Storefront Flat", 0, [], [TenantDocument("ID", False)], [InspectionReminder("2026-11-01")])
    assert follow_up_required(statement) is True
    assert "Status: Follow-up required" in statement_markdown(statement)
    assert "ID: pending" in statement_markdown(statement)
