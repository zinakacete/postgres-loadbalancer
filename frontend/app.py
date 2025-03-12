from flask import Flask, request, render_template, redirect, url_for
import requests
import os

app = Flask(__name__)
server_id = os.getenv('SERVER_ID', '1')
server_id = os.getenv('SERVER_ID')
if not server_id:
    raise ValueError("SERVER_ID n'est pas défini pour frontend")
BACKEND_LB_URL = "http://backend-lb:80"

@app.route('/', methods=['GET'])
def home():
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background: linear-gradient(to right, #6a11cb, #2575fc);
                color: white;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}
            h1 {{
                font-size: 3em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
            }}
            form {{
                background: rgba(0, 0, 0, 0.6);
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.3);
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            input[type="text"] {{
                padding: 10px;
                font-size: 1.2em;
                width: 300px;
                margin-bottom: 20px;
                border: 2px solid #fff;
                border-radius: 5px;
                background: rgba(255, 255, 255, 0.2);
                color: white;
            }}
            button {{
                padding: 12px 30px;
                font-size: 1.2em;
                background: #2575fc;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background 0.3s ease;
            }}
            button:hover {{
                background: #6a11cb;
            }}
            a {{
                margin-top: 20px;
                color: white;
                font-size: 1.1em;
                text-decoration: none;
                transition: color 0.3s ease;
            }}
            a:hover {{
                color: #ff6b6b;
            }}
        </style>
    </head>
    <body>
        <div>
            <h1>Frontend Server {server_id}</h1>
            <form action="/submit" method="post">
                <input type="text" name="data" placeholder="Entrez une donnée">
                <button type="submit">Envoyer</button>
            </form>
            <a href="/data">Voir les données</a>
        </div>
    </body>
    </html>
    """

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Lire les données du formulaire et les transformer en JSON
        data = {
            'message': request.form.get('data', ''),
            'source_server': f"frontend-{server_id}"
        }

        if not data['message']:
            return "Missing required field: message", 400

        # Envoyer correctement les données sous format JSON
        response = requests.post(
            f"{BACKEND_LB_URL}/save",
            json=data,
            headers={'Content-Type': 'application/json'}
        )

        # Vérifier si la réponse du backend est une erreur
        if response.status_code != 200:
            error_message = f"Backend error: Status {response.status_code}, Response: {response.text}"
            print(error_message)
            return error_message, 500

        return redirect('/')

    except Exception as e:
        error_message = f"Error in submit: {str(e)}"
        print(error_message)
        return error_message, 500


@app.route('/data', methods=['GET'])
def show_data():
    try:
        response = requests.get(f"{BACKEND_LB_URL}/data")
        if response.status_code != 200:
            return "Error fetching data", 500

        return f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    background: linear-gradient(to right, #6a11cb, #2575fc);
                    color: white;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                }}
                h1 {{
                    font-size: 3em;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
                }}
                p {{
                    font-size: 1.5em;
                    text-align: center;
                    margin: 20px 0;
                }}
                a {{
                    margin-top: 20px;
                    color: white;
                    font-size: 1.1em;
                    text-decoration: none;
                    transition: color 0.3s ease;
                }}
                a:hover {{
                    color: #ff6b6b;
                }}
            </style>
        </head>
        <body>
            <div>
                <h1>Frontend Server {server_id}</h1>
                <p>Données enregistrées : {response.text}</p>
                <a href="/">Retour</a>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        print(f"Error in show_data: {str(e)}")
        return "Internal server error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)