# qr-forge

**Status: draft** — written from the repo's README and `app/main.py`, not from a
conversation with the owner. Confirm the core job and non-goals, then delete
this line.

## Core job

Someone who needs a QR code — for a WiFi network, a contact card, a URL — gets a
clean SVG or PNG from their own machine, without handing the data to a website.

## Users

Self-hosters running Docker on a home server or workstation. They know how to run
`docker compose up`, they do not want to install anything else, and they reach
for this precisely because the alternative means pasting a WiFi password into a
stranger's web form.

## Success

- A code is produced and downloaded in one visit, with no account and no upload.
- All 8 modes work from the UI: text/URL, WiFi, contact, email, SMS, phone, geo,
  event.
- Output scans correctly on a phone the first time.
- **Time-to-first-result target: 180 seconds** — clone to a scanned code.

## First-run path

1. `git clone https://github.com/williamblair333/qr-forge && cd qr-forge`
2. `docker compose up -d --build`
3. Open `http://localhost:8002`
4. Pick a mode, fill the form, download the SVG.

## Non-goals

- No accounts, no stored history — nothing that would make the data worth keeping.
- No hosted/public deployment; this is a local tool by design.
- No analytics or scan tracking (that would require a redirect service, which is
  a different product).
- No bulk/CSV generation.

## UI principles

- The form is the whole app: no landing page, no navigation to learn.
- Mode switching never loses what was already typed.
- The code updates as the form is filled; the download is one click.
- An invalid field says which field and why, next to the field.
- Dark UI, no external fonts or CDN calls — the page works offline once loaded.

## Verification note

The published path is Docker, but the gate cannot run Docker inside its own
container, so `verify:` exercises the same app the image runs (`uvicorn
app.main:app`) with the same `requirements.txt`. If the Dockerfile and this
block ever disagree about how the app starts, that is a real defect: the gate
would be proving something users never run.

**Known gaps, found while writing this brief:**

- The README documents no way to run this without Docker, even though the image
  itself just runs `uvicorn`. A short "run without Docker" section would close it
  and remove the declared exception below.
- **An unknown query parameter is silently ignored.** `?fmt=bogus` correctly
  returns 400, but `?format=svg` — a plausible guess at the parameter name —
  returns a PNG with 200 OK. The caller believes they asked for SVG and gets
  something else. Rejecting unknown parameters would turn a wrong answer into a
  clear one. (Found by writing this brief's verify block with the wrong name.)

```yaml
verify:
  image: python:3.12-slim
  network: required
  install_note: "README documents `docker compose` only; the gate cannot nest Docker, so it runs the same uvicorn command the image's CMD runs"
  install:
    - pip install --no-cache-dir -r requirements.txt
  run: sh -c "uvicorn app.main:app --host 127.0.0.1 --port 8002 & sleep 5; python3 -c \"import urllib.request; body=urllib.request.urlopen('http://127.0.0.1:8002/qr?data=hello&fmt=svg').read(); open('/tmp/qr-forge.svg','wb').write(body); print(body[:120].decode())\""
  expect:
    - stdout_contains: "<svg"
    - stdout_contains: "200 OK"
    - file: /tmp/qr-forge.svg
    - exit_code: 0
  time_target_seconds: 180
```
