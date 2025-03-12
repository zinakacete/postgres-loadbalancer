from flask import Flask, request ,jsonify
import json

import requests
import os

app = Flask(__name__)
server_id = os.getenv('SERVER_ID', '1')
if not server_id:
    raise ValueError("SERVER_ID n'est pas défini")

if not server_id:
    raise ValueError("SERVER_ID n'est pas défini pour backend ")
DB_LB_URL = "http://db-lb:80"
@app.before_request
def log_request_info():
    print(f"Incoming request: {request.method} {request.url}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {request.get_data()}")

@app.route('/save', methods=['POST'])
def save():
    try:
        # Vérifier si la requête est bien en JSON
        if not request.is_json:
            return jsonify({"error": "Invalid Content-Type, expected JSON"}), 400

        data = request.get_json()
        print("Données reçues par le backend:", data)  # LOG DES DONNÉES REÇUES

        if 'message' not in data:
            return jsonify({
                "error": "Missing required field: message",
                "received_data": data
            }), 400

        # Forward to DB service
        db_payload = json.dumps({'message': data['message']})  # Convertir en JSON
        print("Payload envoyé au DB:", db_payload)  # LOG DES DONNÉES ENVOYÉES

        response = requests.post(
            f"{DB_LB_URL}/save",
            data=db_payload,  # Correction ici : utiliser data au lieu de json
            headers={'Content-Type': 'application/json'}
        )

        print("Réponse reçue de la DB:", response.text)  # LOG RÉPONSE DB

        if response.status_code != 200:
            return jsonify({
                "error": "Database error",
                "db_response": response.text,
                "status_code": response.status_code
            }), response.status_code

        return jsonify({
            "status": "success",
            "server_id": server_id,
            "db_response": response.json()
        }), 200

    except Exception as e:
        print(f"Error in save: {str(e)}")  # LOG ERREUR
        return jsonify({
            "error": str(e),
            "server_id": server_id
        }), 500

# Récupération des données
@app.route('/data')
def get_data():
    response = requests.get(f"{DB_LB_URL}/data")
    return response.text, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
