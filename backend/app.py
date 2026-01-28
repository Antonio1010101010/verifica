from flask import Flask, jsonify
from flask_cors import CORS
from DatabaseWrapper import DatabaseWrapper
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Abilita CORS per tutte le rotte
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Inizializza il database wrapper
db = DatabaseWrapper()


@app.before_request
def before_request():
    """Connette al database prima di ogni richiesta se non già connesso"""
    if not hasattr(app, 'db_connection') or app.db_connection is None:
        db.connect()
        app.db_connection = db.connection
        # Crea le tabelle se non esistono
        db.create_tables()


@app.teardown_appcontext
def teardown_db(error):
    """Chiude la connessione al database alla fine della richiesta"""
    db_connection = getattr(app, 'db_connection', None)
    if db_connection is not None:
        db.close()


@app.route('/api/grades', methods=['GET'])
def get_grades():
    """
    Endpoint GET per recuperare tutti i voti.
    
    Returns:
        JSON: Lista di tutti i voti con informazioni studente e materia
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "student_id": 1,
                    "name": "Mario Rossi",
                    "subject": "Matematica",
                    "grade": 8,
                    "grade_date": "2026-01-28",
                    "created_at": "2026-01-28T10:30:00"
                }
            ]
        }
    """
    try:
        query = """
            SELECT 
                g.id,
                g.student_id,
                s.name,
                g.subject,
                g.grade,
                g.grade_date,
                g.created_at
            FROM grades g
            INNER JOIN students s ON g.student_id = s.id
            ORDER BY g.grade_date DESC, g.created_at DESC
        """
        
        grades = db.execute_query(query)
        
        return jsonify({
            "success": True,
            "data": grades
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint di controllo sanitario per verificare che l'app sia online.
    
    Returns:
        JSON: Stato dell'applicazione
    """
    try:
        # Prova a connettere al database
        db.connect()
        db_status = "connected"
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "ok",
        "database": db_status
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Gestisce errori 404"""
    return jsonify({
        "success": False,
        "error": "Endpoint non trovato"
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Gestisce errori 500"""
    return jsonify({
        "success": False,
        "error": "Errore interno del server"
    }), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_ENV') == 'development'
    )
