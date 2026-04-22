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

```bash
docker build -t airbyte/source-zendesk-custom:dev .
docker run --rm airbyte/source-zendesk-custom:dev spec
```

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
