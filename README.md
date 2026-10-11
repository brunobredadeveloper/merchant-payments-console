# Merchant Payments Console

A fictional merchant backend and dashboard by Bruno Breda. Integrates with `tap-on-phone-demo` to demonstrate persisted idempotency, uncertain payment responses and reconciliation. No real payment rails or card data.

## Run

Python 3.11+; no third-party runtime dependencies.

```sh
python server.py
# Open http://127.0.0.1:8080
python -m unittest -v
```

SQLite stores payments and processed events in `payments.sqlite3` (ignored by Git). Restarting does not lose idempotency. `PAYMENTS_DB`, `HOST`, `PORT` can override defaults.

For Android emulator use `http://10.0.2.2:8080`. For USB device run `adb reverse tcp:8080 tcp:8080` and use `http://127.0.0.1:8080`. The service binds loopback by default. It has no authentication and is a local lab; do not deploy it publicly.

## HTTP contract

| Method | Path | Behavior |
|---|---|---|
| POST | `/api/payments` | JSON `idempotencyKey`, `amountInCents`, `scenario` |
| GET | `/api/payments/by-key/{key}` | Reconcile persisted outcome |
| GET | `/api/payments` | List ledger |
| POST | `/api/payments/{id}/refund` | Idempotent full simulated refund |
| POST | `/api/events` | `eventId`, `paymentId`, `kind`: deduplicate corroborating simulator events |
| GET | `/health` | Service health |

Amounts are BRL integer cents, positive and capped at 1,000,000 BRL. Scenarios: `approve`, `decline`, `lost_response`. A key reused with changed amount or scenario returns 409. Exact replay returns the original payment with 200; first creation returns 201.

`lost_response` commits an approval before delaying the first HTTP response by 5 seconds. Android times out after 2 seconds; query by the original key shows approval. Subsequent identical submissions do not delay or create another charge.

Dashboard shows net approved sales, operation count, refunded total, refunds and duplicate event replay. Its totals constitute a live ledger summary, not a persisted daily settlement or accounting report. Events are simulated through the local API; no external webhook provider is connected.

## Design

`BEGIN IMMEDIATE` plus a unique key makes concurrent retries atomic. Event IDs reject conflicting reuse. Late approval events never undo refunds. SQLite transactions cover mutations and associated ledger events. A refund preserves the original charge identifier.

## Validation and limits

11 automated tests passed: restart replay, concurrent requests, payload conflict, invalid amounts, refund replay, declined refund, event replay/conflict, late event, committed lost-response state and HTTP contract. The HTTP timeout/reconciliation test verifies approval after a lost response. Browser rendering has not been visually verified. No auth, external payment provider, partial refunds, multi-merchant tenancy or scheduled settlement. These are deliberate future extensions.
