# Hackathon runbook

## Before the key arrives

Run the offline checks. They validate request handling and provenance shaping,
but they do not claim Qloo connectivity or a hosted demo.

```powershell
python -m unittest discover -s tests -v
```

## After the key arrives

Set the value in the local shell or an approved secret manager. Do not paste it
into chat, source files, notebooks, screenshots, or issues.

```powershell
$env:QLOO_API_BASE="https://hackathon.api.qloo.com"
$env:QLOO_API_KEY="<set privately>"
python scripts\verify_hackathon_api.py
python app.py
```

Open `http://127.0.0.1:8765`, submit a non-personal Jaipur request, and record
only the redacted result shape and test outcome. A real submission still needs a
publicly reachable demo, repository URL, screenshots or video, and the exact
Devpost fields required by the event. Do not claim those items are complete
until they are actually verified.

## Compute decision

No GPU or TPU is required for the core project: Qloo performs the recommendation
lookup remotely. A Kaggle GPU is justified only for a separately measured local
model component; it should not be started merely to run this API client.

