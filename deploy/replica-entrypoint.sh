#!/bin/sh
set -e
# First boot: clone the primary; -R writes the streaming-replication config.
if [ ! -s "$PGDATA/PG_VERSION" ]; then
  until pg_basebackup -h db-primary -U postgres -D "$PGDATA" -R -X stream; do
    rm -rf "${PGDATA:?}"/*
    sleep 2
  done
  chmod 700 "$PGDATA"
fi
exec postgres -c hot_standby=on
