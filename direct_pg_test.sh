#!/bin/bash

echo "Test direct de PostgreSQL avec et sans load balancing"

# Test sans load balancing (master uniquement)
echo "=== TEST SANS LOAD BALANCING (MASTER UNIQUEMENT) ==="
time for i in {1..100}; do
  docker exec -e PGPASSWORD=postgres pg-master psql -U postgres -d appdb -c "SELECT * FROM voyages;" > /dev/null
done

# Test avec load balancing (simulé)
echo "=== TEST AVEC LOAD BALANCING (TOUS LES SERVEURS) ==="
time for i in {1..100}; do
  server=$([ $((i % 3)) -eq 0 ] && echo "pg-master" || ([ $((i % 3)) -eq 1 ] && echo "pg-replica1" || echo "pg-replica2"))
  docker exec -e PGPASSWORD=postgres $server psql -U postgres -d appdb -c "SELECT * FROM voyages;" > /dev/null
done
