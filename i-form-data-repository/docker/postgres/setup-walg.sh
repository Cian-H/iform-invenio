#!/bin/bash
set -e

if [ "$ENABLE_WALG" = "true" ]; then
    echo "archive_mode = on" >> "$PGDATA/postgresql.conf"
    echo "archive_command = 'wal-g wal-push %p'" >> "$PGDATA/postgresql.conf"
    echo "archive_timeout = 60" >> "$PGDATA/postgresql.conf"
else
    echo "archive_mode = off" >> "$PGDATA/postgresql.conf"
fi
