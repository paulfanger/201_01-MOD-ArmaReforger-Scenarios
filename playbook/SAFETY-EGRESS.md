# SAFETY-EGRESS — Allowed Network Endpoints During Sprint

> Added PHASE META M.5. Active for all autonomous sprint stages.
> Any external HTTP call to a host NOT in this list is a violation.

---

## Allowed Endpoints

| Host | Purpose | Protocol |
|---|---|---|
| `api.anthropic.com` | Anthropic SDK (chat window + Computer Use) | HTTPS |
| `github.com` | Git push/pull/clone | HTTPS |
| `raw.githubusercontent.com` | Raw file access | HTTPS |
| `api.github.com` | gh CLI API calls | HTTPS |
| `community.bistudio.com` | Bohemia wiki — research only | HTTPS |
| `github.com/BohemiaInteractive` | Arma-Reforger-Samples, Script-Diff | HTTPS |
| `reforger.armaplatform.com` | Bohemia news / docs | HTTPS |
| `feedback.bistudio.com` | BI files (log examples etc.) | HTTPS |
| `steamcommunity.com` | Steam — research only | HTTPS |
| `store.steampowered.com` | Steam — research only | HTTPS |
| `pypi.org` + pip indexes | pip install (pre-sprint only, per manifest) | HTTPS |
| `registry.npmjs.org` + npm CDN | npm install (pre-sprint only, per manifest) | HTTPS |

---

## Forbidden

Any host NOT listed above. Examples:
- Personal services (Gmail, Drive, banking, Notion, etc.)
- Cloud storage (Dropbox, OneDrive direct — OK via git)
- Social (Twitter/X, Reddit, Discord API)
- Telemetry endpoints (unless above — e.g. no pypi.org telemetry side-channels)
- Any `localhost` endpoint not explicitly created by the sprint itself

---

## Enforcement

The sprint code must not introduce new HTTP client calls (urllib, requests, httpx, aiohttp)
that target hosts not on this list.

**Auditor check (pre-push):**
```python
# Grep new commits for HTTP calls
git diff HEAD~1..HEAD | grep -E "(requests|httpx|urllib|aiohttp)\.(get|post|put|delete|request)" 
# For each match: verify host is in allowed list above
```

If a non-whitelisted host is found:
1. Sprint stops at next auditor check
2. Escalates to Mac-Opus for review

---

## Testing

```python
# Verify all existing HTTP calls in codebase hit whitelisted hosts:
import re, pathlib
code = pathlib.Path(".").rglob("*.py")
for f in code:
    for line in f.read_text().splitlines():
        if any(k in line for k in ["requests.", "httpx.", "urllib."]):
            print(f.name, line.strip())
```
