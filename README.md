# Airbyte source: Zendesk Support (custom)

Declarative Airbyte source for **Zendesk Support** with a focused stream set:

**No tenant is hardcoded.** Subdomain, credentials, and options come only from the **connection configuration** (Airbyte UI or `--config` JSON). The Docker image and `manifest.yaml` are the same for every user; each connection uses its own config.

| Stream            | Mode        | Notes                                      |
|-------------------|-------------|--------------------------------------------|
| `tags`            | Full refresh| Connection check + lightweight list        |
| `organizations`   | Incremental | `incremental/organizations` + `start_time` |
| `users`           | Incremental | `incremental/users/cursor.json`            |
| `tickets`         | Incremental | Search export API, 30-day `created` slices |
| `ticket_comments` | Incremental | `incremental/ticket_events` + `comment_events` |

Authentication is **API token only** (`email` + `api_token` + `subdomain`). Optional `start_date` bounds incremental replication (default ~730 days if omitted).

## First-time config

Do **not** put shell comments on the same line as `cp` (a bad paste can make words like `fill` / `values` extra arguments and produce `cp: values: Not a directory`).

```bash
mkdir -p secrets
cp secrets/config.example.json secrets/config.json
```

Edit `secrets/config.json` with your real `subdomain`, `email`, and `api_token`.

Or run: `./scripts/bootstrap_config.sh`

**If you see SSL `Hostname mismatch`:** the configured `subdomain` does not match a real Zendesk host (placeholder or typo). Use only the slug — not `https://` and not `.zendesk.com`.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
```

## Docker

The image uses **Python 3.11** (`python:3.11-slim-bookworm`) because **airbyte-cdk 7.x** requires Python **≥ 3.10**; older `airbyte/python-connector-base:1.1.0` is Python 3.9 and will fail at `pip install`.

```bash
docker build -t airbyte/source-zendesk-custom:dev .
docker run --rm airbyte/source-zendesk-custom:dev spec
```

## How to test

### 1. Local (fastest)

```bash
cd airbyte-connector-zendesk
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
```

Optional sample read (writes Airbyte messages to stdout):

```bash
# Use a minimal catalog JSON with one stream; or copy from Airbyte UI after discover.
python main.py read --config secrets/config.json --catalog path/to/catalog.json
```

### 2. Docker image locally

```bash
docker build -t zendesk-custom:test .
docker run --rm zendesk-custom:test spec
docker run --rm -v "$PWD/secrets:/secrets:ro" zendesk-custom:test check --config /secrets/config.json
```

### 3. Self-hosted Airbyte (e.g. airbyte.plumhq.com)

1. **Publish the image** so the cluster can pull it:
   - Push to `main` on GitHub — workflow [Publish Docker image](.github/workflows/docker-publish.yml) builds and pushes to **GHCR**.
   - Open **Actions** on the repo and wait for the workflow to finish (green).
   - If Airbyte cannot pull: in GitHub → **Packages** → the `airbyte-connector-zendesk` package → **Package settings** → set visibility to **Public** (or configure registry auth on your cluster).

2. **In Airbyte UI** → Settings → **Custom connector** (source) → Add:
   - **Docker repository:** `ghcr.io/triptisharma15/airbyte-connector-zendesk`
   - **Docker image tag:** `latest` (or a specific commit SHA from the workflow log)

3. **Sources** → New source → pick your connector → paste the same JSON as `secrets/config.json` → test → save.

4. **Connections** → attach a destination → enable streams → **Sync now** and inspect the job log.

## Config shape

```json
{
  "subdomain": "your_subdomain",
  "credentials": {
    "email": "you@example.com",
    "api_token": "your_token"
  },
  "start_date": "2020-08-01T00:00:00Z",
  "num_workers": 3,
  "page_size": 100
}
```

## Publish to GitHub ([triptisharma15](https://github.com/triptisharma15))

1. On GitHub: **New repository** → name e.g. `airbyte-connector-zendesk` → **Public** → create (no README if you already have commits locally).
2. In this folder:

```bash
git remote add origin https://github.com/triptisharma15/airbyte-connector-zendesk.git
git push -u origin main
```

Use SSH if you prefer: `git@github.com:triptisharma15/airbyte-connector-zendesk.git`

Confirm `secrets/config.json` is **not** listed in `git status` before pushing (it is gitignored).

## Extending

Add stream definitions under `manifest.yaml` `definitions` and list them under `streams`. Custom extractors live in `source_declarative_manifest/components.py` and are referenced via `class_name: source_declarative_manifest.components.YourClass`.
