import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)
server_id = os.getenv('SERVER_ID', '1')
role = os.getenv("ROLE", "replica")

# Configuration de la connexion base de données
db_config = {
    'dbname': 'appdb',
    'user': 'dbuser',
    'password': 'dbpassword',
    'host': f'db{server_id}',  # Se connecter à sa propre instance
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**db_config)

# Initialiser la table si nécessaire (uniquement pour le master)
if role == "master":
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                server VARCHAR(10) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la DB: {str(e)}")

@app.route('/save', methods=['POST'])
def save():
    try:
        # Refuser les écritures sur les replicas
        if role == "replica":
            return jsonify({"error": "This is a replica, only master can write!"}), 403
            
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({"error": "Invalid request format, expected JSON"}), 400
            
        if 'message' not in data:
            return jsonify({"error": "Missing required field: 'message'"}), 400
            
        # Enregistrer dans la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (server, message) VALUES (%s, %s)",
            (f"DB{server_id}", data['message'])
        )
        conn.commit()
        cursor.close()
        conn.close()
            
        return jsonify({"message": f"Donnée '{data['message']}' sauvegardée sur DB {server_id}"}), 200
            
    except Exception as e:
        print(f"ERREUR dans /save DB-{server_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/data', methods=['GET'])
def get_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT server, message, timestamp FROM messages ORDER BY RANDOM() LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
            
        if not result:
            return jsonify({"message": "Aucune donnée enregistrée"}), 200
                
        # Formater la réponse avec l'ID du serveur actuel
        data = {
            "server": f"DB{server_id}",  # Le serveur qui répond
            "message": result[1],        # Le message
            "origin": result[0],         # Le serveur d'origine
            "timestamp": result[2].isoformat()
        }
            
        return jsonify(data), 200
            
    except Exception as e:
        print(f"ERREUR dans /data DB-{server_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)