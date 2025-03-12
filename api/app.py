from flask import Flask, jsonify
import psycopg2
import random

app = Flask(__name__)

# Connexion au master
def get_master_connection():
    return psycopg2.connect(
        dbname="appdb",
        user="postgres",
        password="postgres",
        host="pg-master",
        port="5432"
    )

# Connexion aléatoire à un serveur (load balancing)
def get_random_connection():
    servers = ["pg-master", "pg-replica1", "pg-replica2"]
    server = random.choice(servers)
    return psycopg2.connect(
        dbname="appdb",
        user="postgres",
        password="postgres",
        host=server,
        port="5432"
    )

# Endpoint avec load balancing
@app.route('/pg_voyages')
def get_voyages():
    conn = get_random_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voyages")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify(result)

# Endpoint pour écriture - toujours vers le master
@app.route('/pg_voyages_write', methods=['POST'])
def write_voyages():
    conn = get_master_connection()
    # Logique d'insertion ici...
    return jsonify({"success": True})

# Endpoint sans load balancing - toujours vers le master
@app.route('/pg_voyages_single')
def get_voyages_single():
    conn = get_master_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voyages")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    result = [dict(zip(columns, row)) for row in rows]
    cursor.close()
    conn.close()
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)