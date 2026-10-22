# TasteTrail Jaipur

TasteTrail is a small, evidence-first itinerary planner for the Qloo Agentic
Hackathon. A user supplies a location, interests, budget, time window, and hard
constraints. The server resolves the interest phrases with Qloo entity search,
requests location-scoped recommendations from the Qloo Insights API, and
returns a short list with affinity and provenance fields.

## Current status

This is a CPU-checked deployment package. It is **not yet a verified live demo**:
the Qloo API key and a public host are still required. Do not describe this as a
working Qloo submission until a fresh live smoke test passes.

## Repository layout

- `app.py` — dependency-free local web UI and JSON endpoint.
- `tastetrail/core.py` — validation and provenance-preserving response shaping.
- `tastetrail/qloo.py` — server-side Qloo API client.
- `scripts/verify_hackathon_api.py` — redacted live connectivity check.
- `tests/` — offline tests using a fake client; no credentials or network calls.

## Run locally

```powershell
$env:QLOO_API_KEY = "your-key-in-the-host-secret-store"
python app.py
```

Open `http://127.0.0.1:8765`. The key is read only from `QLOO_API_KEY`; never
commit it or put it in a public README. `GET /health` reports whether a key is
configured without revealing it.

## API contract

The client uses the public Qloo API v2 endpoints documented in Qloo's public
documentation: `GET /search` for entity resolution and `GET /v2/insights` for
recommendation insights, authenticated by the `x-api-key` header. Hackathon
credentials must use `https://hackathon.api.qloo.com`; staging and production
hosts are not interchangeable. The exact response is preserved only as
normalized recommendation fields; raw secrets are never returned.

## Checks

```powershell
python -m unittest discover -s tests -v
```

The tests use a local fake client and do not claim that the real API, hosting,
or hackathon submission has been validated.

## When the key arrives

Keep the key in the shell or an approved secret store. Do not paste it into
chat, source files, notebooks, or screenshots. From this directory, run the
redacted connectivity check:

```powershell
$env:QLOO_API_BASE = "https://hackathon.api.qloo.com"
$env:QLOO_API_KEY = "<set privately from the email>"
python scripts/verify_hackathon_api.py
```

The check calls only `/search` and prints the response shape, never the key or
raw Qloo data. A passing check is API connectivity evidence; it is not yet
evidence of a hosted demo or a valid competition submission.

`QLOO_BASE_URL` is also accepted for compatibility with the official Qloo
harness instructions. The client still defaults to the hackathon host and does
not accept a production key as a substitute.

## License

MIT. Qloo remains the upstream API and service provider; any additional assets
must retain their own attribution and license notices.

