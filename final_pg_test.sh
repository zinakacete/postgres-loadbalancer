#!/bin/bash

# Test avec une requête plus complexe et plus de données
echo "=== Création d'une table plus grande pour le test ==="
docker exec -e PGPASSWORD=postgres pg-master psql -U postgres -d appdb -c "
CREATE TABLE IF NOT EXISTS big_data AS
SELECT 
    generate_series(1, 100000) AS id,
    md5(random()::text) AS data_hash,
    random() * 1000 AS value,
    (ARRAY['Paris', 'New York', 'Tokyo', 'Londres', 'Barcelone'])[floor(random() * 5 + 1)] AS city
;"

# Fonction pour exécuter une requête complexe directement sur un serveur spécifique
run_direct_query() {
    server=$1
    echo "Exécution directe sur $server..."
    start_time=$(date +%s.%N)
    
    docker exec -e PGPASSWORD=postgres $server psql -U postgres -d appdb -c "
    SELECT 
        city, 
        COUNT(*), 
        AVG(value), 
        SUM(value), 
        MIN(value), 
        MAX(value),
        VARIANCE(value)
    FROM big_data
    GROUP BY city
    ORDER BY city;
    " > /dev/null
    
    end_time=$(date +%s.%N)
    execution_time=$(echo "$end_time - $start_time" | bc)
    echo "Temps d'exécution: $execution_time secondes"
}

# Fonction pour exécuter des requêtes parallèles sans load balancing (uniquement sur master)
run_parallel_master() {
    num_queries=$1
    echo "Exécution de $num_queries requêtes parallèles sur master uniquement..."
    start_time=$(date +%s.%N)
    
    for i in $(seq 1 $num_queries); do
        docker exec -e PGPASSWORD=postgres pg-master psql -U postgres -d appdb -c "
        SELECT 
            city, 
            COUNT(*), 
            AVG(value), 
            SUM(value), 
            MIN(value), 
            MAX(value),
            VARIANCE(value)
        FROM big_data
        GROUP BY city
        ORDER BY city;
        " > /dev/null &
    done
    wait
    
    end_time=$(date +%s.%N)
    execution_time=$(echo "$end_time - $start_time" | bc)
    echo "Temps d'exécution total: $execution_time secondes"
}

# Fonction pour exécuter des requêtes en parallèle avec load balancing
# Utiliser votre point d'entrée de load balancer ou simuler en distribuant manuellement
run_parallel_loadbalanced() {
    num_queries=$1
    echo "Exécution de $num_queries requêtes avec load balancing..."
    start_time=$(date +%s.%N)
    
    # Si vous avez un point d'entrée unique pour votre load balancer, utilisez celui-ci
    # Sinon, nous distribuons manuellement entre les 3 serveurs pour simuler
    servers=("pg-master" "pg-replica1" "pg-replica2")
    
    for i in $(seq 1 $num_queries); do
        # Choisir un serveur en round-robin pour simuler le load balancing
        server_index=$((i % 3))
        server=${servers[$server_index]}
        
        docker exec -e PGPASSWORD=postgres $server psql -U postgres -d appdb -c "
        SELECT 
            city, 
            COUNT(*), 
            AVG(value), 
            SUM(value), 
            MIN(value), 
            MAX(value),
            VARIANCE(value)
        FROM big_data
        GROUP BY city
        ORDER BY city;
        " > /dev/null &
    done
    wait
    
    end_time=$(date +%s.%N)
    execution_time=$(echo "$end_time - $start_time" | bc)
    echo "Temps d'exécution total: $execution_time secondes"
}

# Test des serveurs individuels
echo ""
echo "=== TESTS INDIVIDUELS DES SERVEURS ==="
echo "Master:"
run_direct_query "pg-master"
echo "Replica 1:"
run_direct_query "pg-replica1"
echo "Replica 2:"
run_direct_query "pg-replica2"

# Test de charge faible (10 requêtes parallèles)
echo ""
echo "=== TEST DE CHARGE FAIBLE (10 requêtes parallèles) ==="
echo "Sans load balancing (master uniquement):"
run_parallel_master 10
echo "Avec load balancing (distribution entre tous les serveurs):"
run_parallel_loadbalanced 10

# Test de charge moyenne (30 requêtes parallèles)
echo ""
echo "=== TEST DE CHARGE MOYENNE (30 requêtes parallèles) ==="
echo "Sans load balancing (master uniquement):"
run_parallel_master 30
echo "Avec load balancing (distribution entre tous les serveurs):"
run_parallel_loadbalanced 30

# Test de charge élevée (100 requêtes parallèles)
echo ""
echo "=== TEST DE CHARGE ÉLEVÉE (100 requêtes parallèles) ==="
echo "Sans load balancing (master uniquement):"
run_parallel_master 100
echo "Avec load balancing (distribution entre tous les serveurs):"
run_parallel_loadbalanced 100

# Ajouter un test avec une charge beaucoup plus élevée
echo ""
echo "=== TEST DE CHARGE TRÈS ÉLEVÉE (500 requêtes parallèles) ==="
echo "Sans load balancing (master uniquement):"
run_parallel_master 500
echo "Avec load balancing (distribution entre tous les serveurs):"
run_parallel_loadbalanced 500

# Ajouter un test de requête plus complexe
run_complex_query() {
    # Requête qui génère une charge plus importante
    docker exec -e PGPASSWORD=postgres $1 psql -U postgres -d appdb -c "
    WITH ranked_data AS (
        SELECT 
            id, 
            city,
            value,
            ROW_NUMBER() OVER (PARTITION BY city ORDER BY value DESC) as rank
        FROM big_data
    )
    SELECT 
        city, 
        AVG(value) as avg_value,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value) as median,
        STDDEV(value) as std_dev,
        COUNT(*) as count
    FROM ranked_data
    WHERE rank <= 1000
    GROUP BY city
    ORDER BY avg_value DESC;
    " > /dev/null
}