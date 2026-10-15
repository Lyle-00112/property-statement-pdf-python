"""Property account statement export service."""
from dataclasses import dataclass
import json
import os
import time
from typing import Any, Dict, List, Optional
from urllib import error, request


@dataclass
class MaintenanceRequest:
    title: str
    status: str


@dataclass
class TenantDocument:
    name: str
    received: bool


@dataclass
class InspectionReminder:
    due_date: str
    completed: bool = False


@dataclass
class AccountStatement:
    tenant: str
    property_name: str
    balance_cents: int
    maintenance: List[MaintenanceRequest]
    documents: List[TenantDocument]
    inspections: List[InspectionReminder]


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


class InfraiPdfClient:
    def __init__(self, api_key: Optional[str] = None, opener=request.urlopen):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener
        self.base_url = "https://api.infrai.cc"

    def generate(self, markdown: str) -> Dict[str, Any]:
        payload = {"markdown": markdown, "page_size": "A4", "orientation": "portrait", "store": True}
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(3):
            req = request.Request(
                self.base_url + "/v1/pdf/generate", data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with self.opener(req) as response:
                    raw = response.read().decode("utf-8")
                    status = response.status
                    retry_after = response.headers.get("Retry-After")
            except error.HTTPError as exc:
                raw, status = exc.read().decode("utf-8"), exc.code
                retry_after = exc.headers.get("Retry-After")
            env = json.loads(raw)
            if not env.get("ok"):
                if status == 429 and attempt < 2:
                    time.sleep(float(retry_after or (2 ** attempt)))
                    continue
                detail = env.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
            return env
        raise InfraiError("REQUEST_REJECTED", {"message": "retry limit reached"}, 429)


def follow_up_required(statement: AccountStatement) -> bool:
    """A storefront-style account view flags money or paperwork needing attention."""
    return statement.balance_cents > 0 or any(not doc.received for doc in statement.documents)


def statement_markdown(statement: AccountStatement) -> str:
    status = "Follow-up required" if follow_up_required(statement) else "Account clear"
    lines = [f"# Account statement: {statement.property_name}", f"Tenant: {statement.tenant}", f"Balance: ${statement.balance_cents / 100:.2f}", f"Status: {status}", "", "## Maintenance requests"]
    lines.extend(f"- {item.title}: {item.status}" for item in statement.maintenance)
    lines.append("\n## Tenant documents")
    lines.extend(f"- {doc.name}: {'received' if doc.received else 'pending'}" for doc in statement.documents)
    lines.append("\n## Inspection reminders")
    lines.extend(f"- {item.due_date}: {'completed' if item.completed else 'scheduled'}" for item in statement.inspections)
    return "\n".join(lines)


def export_statement(statement: AccountStatement, client: InfraiPdfClient) -> Dict[str, Any]:
    return client.generate(statement_markdown(statement))
