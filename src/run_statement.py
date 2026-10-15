from statement_service import AccountStatement, InspectionReminder, MaintenanceRequest, TenantDocument, InfraiPdfClient, export_statement


def main() -> None:
    statement = AccountStatement(
        tenant="Mina Chen", property_name="Harbor View 204", balance_cents=12500,
        maintenance=[MaintenanceRequest("Leaking kitchen tap", "scheduled")],
        documents=[TenantDocument("Proof of insurance", False)],
        inspections=[InspectionReminder("2026-10-15")],
    )
    result = export_statement(statement, InfraiPdfClient())
    print(result["data"])


if __name__ == "__main__":
    main()
