#!/bin/sh
set -e
chown -R oryantasyonappuser:oryantasyonappuser /app/oryantasyonfiles /app/oryantasyongorseller /app/config.json
exec gosu oryantasyonappuser "$@"
