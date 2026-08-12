#!/bin/bash
set -e

# Configure postgres to archive WAL logs via wal-g
echo "archive_mode = on" >> "$PGDATA/postgresql.conf"
echo "archive_command = 'wal-g wal-push %p'" >> "$PGDATA/postgresql.conf"
echo "archive_timeout = 60" >> "$PGDATA/postgresql.conf"
