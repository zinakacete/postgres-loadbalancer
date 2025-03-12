#!/bin/bash
set -e

echo "Configuring PostgreSQL master..."

# Configuration pour permettre la réplication
cat >> "${PGDATA}/postgresql.conf" << EOF
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
synchronous_commit = on
wal_keep_size = 1GB
EOF

# Autorisations pour la réplication
cat >> "${PGDATA}/pg_hba.conf" << EOF
host replication dbuser all md5
host replication dbuser 0.0.0.0/0 md5
EOF

echo "Master configuration complete!"

# Créer des slots de réplication (après le démarrage complet)
psql -U postgres -c "SELECT pg_create_physical_replication_slot('replica_sys-avance-db2-1');"
psql -U postgres -c "SELECT pg_create_physical_replication_slot('replica_sys-avance-db3-1');"