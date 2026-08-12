#!/bin/bash
set -e

# Start the cron service in the background
service cron start

# Pass execution back to the official postgres entrypoint
exec /usr/local/bin/docker-entrypoint.sh "$@"
