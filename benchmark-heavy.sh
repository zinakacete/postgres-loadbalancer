#!/bin/bash

# Configurations
PG_TEST_RUNS=3
PG_REQUESTS=100  # Réduit pour le test initial
PG_CONCURRENCY=10
PG_PASSWORD="postgres"  # Mot de passe défini dans docker-compose.yml

# Fonction pour tester une connexion PostgreSQL
test_pg_connection() {
    server=$1
    test_name=$2
    output_file="pg_results_${test_name}.txt"
    
    echo "Test de connexion PostgreSQL sur $server - $test_name"
    echo "-------------------------------------------------" | tee $output_file
    echo "Date: $(date)" | tee -a $output_file
    echo "Serveur: $server" | tee -a $output_file
    echo "-------------------------------------------------" | tee -a $output_file
    
    # Exécuter les requêtes multiples fois et mesurer le temps
    for i in $(seq 1 $PG_TEST_RUNS); do
        echo "Test run #$i" | tee -a $output_file
        start_time=$(date +%s.%N)
        
        # Exécuter plusieurs requêtes SQL en parallèle (simuler la charge)
        for j in $(seq 1 $PG_REQUESTS); do
            docker exec pg-master psql -U postgres -d appdb -c "SELECT * FROM voyages;" -W $PG_PASSWORD > /dev/null 2>&1 &
            
            # Limiter la concurrence
            if [ $((j % $PG_CONCURRENCY)) -eq 0 ]; then
                wait
            fi
        done
        wait
        
        end_time=$(date +%s.%N)
        execution_time=$(echo "$end_time - $start_time" | bc)
        echo "Temps d'exécution: $execution_time secondes" | tee -a $output_file
        echo "Requêtes par seconde: $(echo "$PG_REQUESTS / $execution_time" | bc)" | tee -a $output_file
        echo "-------------------------------------------------" | tee -a $output_file
    done
    
    # Afficher un résumé
    echo "Résultats pour $test_name enregistrés dans $output_file"
}

# Approche alternative: utiliser PGPASSWORD
test_pg_connection_with_password() {
    server=$1
    test_name=$2
    output_file="pg_results_${test_name}.txt"
    
    echo "Test de connexion PostgreSQL sur $server - $test_name"
    echo "-------------------------------------------------" | tee $output_file
    echo "Date: $(date)" | tee -a $output_file
    echo "Serveur: $server" | tee -a $output_file
    echo "-------------------------------------------------" | tee -a $output_file
    
    # Exécuter les requêtes multiples fois et mesurer le temps
    for i in $(seq 1 $PG_TEST_RUNS); do
        echo "Test run #$i" | tee -a $output_file
        start_time=$(date +%s.%N)
        
        # Exécuter plusieurs requêtes SQL en parallèle avec PGPASSWORD
        for j in $(seq 1 $PG_REQUESTS); do
            docker exec -e PGPASSWORD=$PG_PASSWORD pg-master psql -U postgres -d appdb -c "SELECT * FROM voyages;" > /dev/null 2>&1 &
            
            # Limiter la concurrence
            if [ $((j % $PG_CONCURRENCY)) -eq 0 ]; then
                wait
            fi
        done
        wait
        
        end_time=$(date +%s.%N)
        execution_time=$(echo "$end_time - $start_time" | bc)
        echo "Temps d'exécution: $execution_time secondes" | tee -a $output_file
        echo "Requêtes par seconde: $(echo "$PG_REQUESTS / $execution_time" | bc)" | tee -a $output_file
        echo "-------------------------------------------------" | tee -a $output_file
    done
    
    # Afficher un résumé
    echo "Résultats pour $test_name enregistrés dans $output_file"
}

# 1. Test en utilisant uniquement le master (avec mot de passe)
echo "=== Test PostgreSQL sans load balancing (master uniquement) ==="
test_pg_connection_with_password "pg-master" "no_lb"

# 2. Test en utilisant tous les serveurs avec load balancing
echo "=== Test PostgreSQL avec load balancing (tous les serveurs) ==="
servers=("pg-master" "pg-replica1" "pg-replica2")
server_index=0

# Fonction pour obtenir le prochain serveur dans la rotation
get_next_server() {
    server=${servers[$server_index]}
    server_index=$(( (server_index + 1) % ${#servers[@]} ))
    echo $server
}

# Exécuter le test avec rotation des serveurs
test_pg_connection_lb_with_password() {
    test_name="with_lb"
    output_file="pg_results_${test_name}.txt"
    
    echo "Test de connexion PostgreSQL avec load balancing"
    echo "-------------------------------------------------" | tee $output_file
    echo "Date: $(date)" | tee -a $output_file
    echo "Serveurs: ${servers[*]}" | tee -a $output_file
    echo "-------------------------------------------------" | tee -a $output_file
    
    # Exécuter les requêtes multiples fois et mesurer le temps
    for i in $(seq 1 $PG_TEST_RUNS); do
        echo "Test run #$i" | tee -a $output_file
        start_time=$(date +%s.%N)
        
        # Exécuter plusieurs requêtes SQL en parallèle (simuler la charge)
        for j in $(seq 1 $PG_REQUESTS); do
            server=$(get_next_server)
            docker exec -e PGPASSWORD=$PG_PASSWORD $server psql -U postgres -d appdb -c "SELECT * FROM voyages;" > /dev/null 2>&1 &
            
            # Limiter la concurrence
            if [ $((j % $PG_CONCURRENCY)) -eq 0 ]; then
                wait
            fi
        done
        wait
        
        end_time=$(date +%s.%N)
        execution_time=$(echo "$end_time - $start_time" | bc)
        echo "Temps d'exécution: $execution_time secondes" | tee -a $output_file
        echo "Requêtes par seconde: $(echo "$PG_REQUESTS / $execution_time" | bc)" | tee -a $output_file
        echo "-------------------------------------------------" | tee -a $output_file
    done
    
    # Afficher un résumé
    echo "Résultats pour $test_name enregistrés dans $output_file"
}

test_pg_connection_lb_with_password

echo "Tests PostgreSQL terminés. Consultez les fichiers pg_results_*.txt pour les détails."