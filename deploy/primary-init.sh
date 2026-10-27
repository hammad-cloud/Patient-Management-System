#!/bin/sh
# Allow the read replica to stream WAL from this primary.
echo "host replication all all scram-sha-256" >> "$PGDATA/pg_hba.conf"
