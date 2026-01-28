from flask import Flask, jsonify, request
from flask_cors import CORS
from DatabaseWrapper import DatabaseWrapper
import os
from dotenv import load_dotenv
from datetime import datetime

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


@app.route('/api/grades', methods=['POST'])
def create_grade():
    """
    Endpoint POST per inserire un nuovo voto.
    
    Request body (JSON):
    {
        "student_name": "Mario Rossi",
        "subject": "Matematica",
        "grade": 8,
        "grade_date": "2026-01-28"
    }
    
    Returns:
        JSON: Dati del voto creato
        {
            "success": true,
            "data": {
                "id": 1,
                "student_id": 1,
                "student_name": "Mario Rossi",
                "subject": "Matematica",
                "grade": 8,
                "grade_date": "2026-01-28"
            }
        }
    """
    try:
        data = request.get_json()
        
        # Validazioni minime
        errors = []
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Corpo della richiesta vuoto"
            }), 400
        
        # Controllo campi obbligatori
        if not data.get('student_name') or not data['student_name'].strip():
            errors.append("student_name è obbligatorio")
        
        if not data.get('subject') or not data['subject'].strip():
            errors.append("subject è obbligatorio")
        
        if 'grade' not in data:
            errors.append("grade è obbligatorio")
        else:
            # Validazione voto: deve essere un numero tra 0 e 10
            try:
                grade = int(data['grade'])
                if grade < 0 or grade > 10:
                    errors.append("grade deve essere compreso tra 0 e 10")
            except (ValueError, TypeError):
                errors.append("grade deve essere un numero intero")
        
        if not data.get('grade_date') or not data['grade_date'].strip():
            errors.append("grade_date è obbligatorio")
        else:
            # Validazione formato data (YYYY-MM-DD)
            try:
                datetime.strptime(data['grade_date'], '%Y-%m-%d')
            except ValueError:
                errors.append("grade_date deve essere nel formato YYYY-MM-DD")
        
        if errors:
            return jsonify({
                "success": False,
                "errors": errors
            }), 400
        
        # Ricerca o creazione dello studente
        student_name = data['student_name'].strip()
        query_student = "SELECT id FROM students WHERE name = %s"
        existing_student = db.execute_query(query_student, (student_name,))
        
        if existing_student:
            student_id = existing_student[0]['id']
        else:
            # Inserisci nuovo studente
            query_insert_student = "INSERT INTO students (name) VALUES (%s)"
            student_id = db.execute_insert(query_insert_student, (student_name,))
        
        # Inserisci il voto
        query_insert_grade = """
            INSERT INTO grades (student_id, subject, grade, grade_date)
            VALUES (%s, %s, %s, %s)
        """
        grade_id = db.execute_insert(
            query_insert_grade,
            (student_id, data['subject'].strip(), int(data['grade']), data['grade_date'])
        )
        
        return jsonify({
            "success": True,
            "data": {
                "id": grade_id,
                "student_id": student_id,
                "student_name": student_name,
                "subject": data['subject'].strip(),
                "grade": int(data['grade']),
                "grade_date": data['grade_date']
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/grades/<int:grade_id>', methods=['PUT'])
def update_grade(grade_id):
    """
    Endpoint PUT per modificare un voto esistente.
    
    URL Parameter:
        grade_id: ID del voto da modificare
    
    Request body (JSON) - tutti i campi sono opzionali:
    {
        "subject": "Matematica",
        "grade": 8,
        "grade_date": "2026-01-28"
    }
    
    Returns:
        JSON: Dati del voto modificato
        {
            "success": true,
            "data": {
                "id": 1,
                "subject": "Matematica",
                "grade": 8,
                "grade_date": "2026-01-28"
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Corpo della richiesta vuoto"
            }), 400
        
        # Verifica che il voto esista
        query_check = "SELECT id FROM grades WHERE id = %s"
        existing_grade = db.execute_query(query_check, (grade_id,))
        
        if not existing_grade:
            return jsonify({
                "success": False,
                "error": f"Voto con ID {grade_id} non trovato"
            }), 404
        
        # Validazioni e costruzione query UPDATE
        updates = []
        params = []
        errors = []
        
        # Validazione subject (opzionale)
        if 'subject' in data:
            if data['subject'] and data['subject'].strip():
                updates.append("subject = %s")
                params.append(data['subject'].strip())
            else:
                errors.append("subject non può essere vuoto")
        
        # Validazione grade (opzionale)
        if 'grade' in data:
            try:
                grade = int(data['grade'])
                if grade < 0 or grade > 10:
                    errors.append("grade deve essere compreso tra 0 e 10")
                else:
                    updates.append("grade = %s")
                    params.append(grade)
            except (ValueError, TypeError):
                errors.append("grade deve essere un numero intero")
        
        # Validazione grade_date (opzionale)
        if 'grade_date' in data:
            if data['grade_date'] and data['grade_date'].strip():
                try:
                    datetime.strptime(data['grade_date'], '%Y-%m-%d')
                    updates.append("grade_date = %s")
                    params.append(data['grade_date'])
                except ValueError:
                    errors.append("grade_date deve essere nel formato YYYY-MM-DD")
            else:
                errors.append("grade_date non può essere vuoto")
        
        if errors:
            return jsonify({
                "success": False,
                "errors": errors
            }), 400
        
        if not updates:
            return jsonify({
                "success": False,
                "error": "Nessun campo da aggiornare"
            }), 400
        
        # Esegui l'UPDATE
        params.append(grade_id)
        query_update = f"UPDATE grades SET {', '.join(updates)} WHERE id = %s"
        db.execute_update(query_update, tuple(params))
        
        # Recupera il voto aggiornato
        query_get = """
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
            WHERE g.id = %s
        """
        updated_grade = db.execute_query(query_get, (grade_id,))
        
        if updated_grade:
            return jsonify({
                "success": True,
                "data": updated_grade[0]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Errore nel recuperare il voto aggiornato"
            }), 500
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/grades/<int:grade_id>', methods=['GET'])
def get_single_grade(grade_id):
    """
    Endpoint GET per recuperare un singolo voto.
    
    URL Parameter:
        grade_id: ID del voto da recuperare
    
    Returns:
        JSON: Dati del voto
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
            WHERE g.id = %s
        """
        
        grade = db.execute_query(query, (grade_id,))
        
        if grade:
            return jsonify({
                "success": True,
                "data": grade[0]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": f"Voto con ID {grade_id} non trovato"
            }), 404
        
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
