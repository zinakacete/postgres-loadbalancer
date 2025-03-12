#!/bin/bash
set -e

echo "Starting PostgreSQL replica initialization..."

# Attendre que le master soit disponible
until PGPASSWORD=dbpassword psql -h db1 -U dbuser -d appdb -c '\q'; do
  >&2 echo "Waiting for master database..."
  sleep 5
done

# Vider le répertoire de données
rm -rf ${PGDATA}/*

# Initialiser le replica depuis le master avec les paramètres de réplication
PGPASSWORD=dbpassword pg_basebackup -h db1 -U dbuser -D ${PGDATA} -P -v -X stream -R

# Configuration supplémentaire pour le standby (PostgreSQL 14)
cat >> "${PGDATA}/postgresql.conf" << EOF
primary_conninfo = 'host=db1 port=5432 user=dbuser password=dbpassword application_name=replica'
primary_slot_name = 'replica_$(hostname)'
hot_standby = on
EOF

# Créer le fichier standby.signal pour indiquer que c'est un replica
touch ${PGDATA}/standby.signal

echo "Replica initialization complete!"