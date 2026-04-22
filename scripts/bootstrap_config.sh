#!/usr/bin/env sh
set -e
cd "$(dirname "$0")/.."
mkdir -p secrets
if [ -f secrets/config.json ]; then
  echo "secrets/config.json already exists — remove it first if you want a fresh copy."
  exit 0
fi
cp secrets/config.example.json secrets/config.json
echo "Created secrets/config.json — edit it with your Zendesk subdomain and API token."
