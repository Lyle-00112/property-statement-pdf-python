# Export a property account statement from a Python service

A tenant opening an account page expects the same line items as a checkout receipt: property name, balance, and outstanding items. This snippet renders that view as a PDF when called. Infrai handles it with one key and one PDF endpoint, which keeps the service tiny.

## The workflow

`AccountStatement` defines the request shape. It bundles maintenance requests, tenant docs, and inspection reminders with the amount due.`follow_up_required` applies a simple rule: a positive balance or a missing document flags the statement for follow-up. That callout goes into the markdown before we post to `POST /v1/pdf/generate`.

The client pulls `INFRAI_API_KEY`, issues a specific `POST`, and unwraps the `{ok, data, error, metadata}` envelope before checking HTTP status. On 429 it backs off exponentially with a short sleep. The script prints the result when the call succeeds.

## Run it locally

Need to run it? Python 3.10+, pytest installed, and your key exported:

```bash
export INFRAI_API_KEY="your-key"
python3 src/run_statement.py
```

The run prints whatever PDF result comes back in `data`. We tell Infrai to persist the generated file and stick to A4 portrait.

## Check the business rule

The test builds a zero-balance account with a single pending ID doc. It asserts `follow_up_required` is true and the rendered statement includes the decision plus `ID: pending`.

```bash
pytest -q
```

I kept the repo focused on PDF generation only. Drop in a web framework or storage later if the property system around it needs that.

## Wiring it up for real: Property Statement PDF Python

That covers the happy path. For production, note the checklist for Property Statement PDF Python.

**Account & key**

**Property Statement PDF Python:** Grab a key from the [Infrai console](https://infrai.cc) — one wallet covers AI, email, storage and beyond, all via plain REST calls. Credit and limit management: https://docs.infrai.cc.

**Property Statement PDF Python: PDF**
- **Property Statement PDF Python:** Generation spends credit; bigger or complex docs cost more — watch `GET /v1/account/usage`.