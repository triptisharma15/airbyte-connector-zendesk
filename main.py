#!/usr/bin/env python3
"""Airbyte entrypoint for the custom Zendesk Support source."""

import json
import os
import sys
from typing import Any, Dict, Optional, Tuple

from airbyte_cdk.entrypoint import launch
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

# Example / doc hostnames — using them causes TLS "hostname mismatch" (not Zendesk).
_PLACEHOLDER_SUBDOMAINS = frozenset(
    {
        "",
        "your_subdomain",
        "your_subdomain_here",
        "placeholder",
        "changeme",
        "YOUR_SUBDOMAIN",
    }
)


def _command_hits_zendesk_api(argv: list) -> bool:
    return any(a in argv for a in ("check", "discover", "read"))


def _validate_config_for_api_calls(config: Dict[str, Any]) -> None:
    if not config:
        return
    sub = str(config.get("subdomain") or "").strip()
    if sub in _PLACEHOLDER_SUBDOMAINS or sub.upper() == "YOUR_SUBDOMAIN":
        print(
            "Invalid config: `subdomain` is still a placeholder.\n"
            "Each Airbyte connection supplies its own JSON: set `subdomain` to that account's Zendesk slug only "
            "(the part before `.zendesk.com`, e.g. `mycompany` for https://mycompany.zendesk.com).\n"
            "Do not include `https://` or `.zendesk.com` in the subdomain field.\n"
            "SSL hostname mismatch usually means this value is wrong or still a template.",
            file=sys.stderr,
        )
        sys.exit(1)
    creds = config.get("credentials") or {}
    token = str(creds.get("api_token") or "").strip()
    email = str(creds.get("email") or "").strip()
    if not token or token == "YOUR_ZENDESK_API_TOKEN":
        print(
            "Invalid config: set `credentials.api_token` to your real Zendesk API token.",
            file=sys.stderr,
        )
        sys.exit(1)
    if not email:
        print(
            "Invalid config: set `credentials.email` to the Zendesk agent email used with the API token.",
            file=sys.stderr,
        )
        sys.exit(1)
    if email.strip().lower() == "you@example.com":
        print(
            "Invalid config: `credentials.email` is still the template value from config.example.json; "
            "replace it with the real agent email for this Zendesk account.",
            file=sys.stderr,
        )
        sys.exit(1)


def _load_config() -> Tuple[Dict[str, Any], Optional[str]]:
    config: Dict[str, Any] = {}
    config_path: Optional[str] = None
    for i, arg in enumerate(sys.argv):
        if arg == "--config" and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 1]
            if not os.path.isfile(config_path):
                print(
                    f"Config file not found: {config_path}\n"
                    "Create it first, for example:\n"
                    "  mkdir -p secrets\n"
                    "  cp secrets/config.example.json secrets/config.json\n"
                    "Then edit secrets/config.json with your subdomain and API token.",
                    file=sys.stderr,
                )
                sys.exit(1)
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
            break
    return config, config_path


if __name__ == "__main__":
    cfg, path = _load_config()
    if path and _command_hits_zendesk_api(sys.argv):
        _validate_config_for_api_calls(cfg)
    source = YamlDeclarativeSource(
        path_to_yaml="manifest.yaml",
        config=cfg,
        config_path=path,
    )
    launch(source, sys.argv[1:])
