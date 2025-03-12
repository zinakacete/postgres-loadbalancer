#!/bin/bash

REQUESTS=1000  # Augmentation significative du nombre de requêtes
CONCURRENCY=10  # Exécution de requêtes en parallèle

echo "Test intensif de PostgreSQL avec et sans load balancing"

# Test sans load balancing (master uniquement)
echo "=== TEST SANS LOAD BALANCING (MASTER UNIQUEMENT) ==="
start_time=$(date +%s.%N)

for i in $(seq 1 $CONCURRENCY); do
  (
    for j in $(seq 1 $(($REQUESTS / $CONCURRENCY))); do
      docker exec -e PGPASSWORD=postgres pg-master psql -U postgres -d appdb -c "SELECT * FROM voyages;" > /dev/null
    done
  ) &
done
wait

end_time=$(date +%s.%N)
execution_time=$(echo "$end_time - $start_time" | bc)
echo "Temps d'exécution: $execution_time secondes"
echo "Requêtes par seconde: $(echo "$REQUESTS / $execution_time" | bc)"

# Test avec load balancing (simulé)
echo ""
echo "=== TEST AVEC LOAD BALANCING (TOUS LES SERVEURS) ==="
servers=("pg-master" "pg-replica1" "pg-replica2")
server_index=0
start_time=$(date +%s.%N)

for i in $(seq 1 $CONCURRENCY); do
  (
    for j in $(seq 1 $(($REQUESTS / $CONCURRENCY))); do
      server=${servers[$(($j % 3))]}
      docker exec -e PGPASSWORD=postgres $server psql -U postgres -d appdb -c "SELECT * FROM voyages;" > /dev/null
    done
  ) &
done
wait

end_time=$(date +%s.%N)
execution_time=$(echo "$end_time - $start_time" | bc)
echo "Temps d'exécution: $execution_time secondes"
echo "Requêtes par seconde: $(echo "$REQUESTS / $execution_time" | bc)"
