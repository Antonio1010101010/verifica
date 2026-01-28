import pymysql
from pymysql.cursors import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseWrapper:
    """
    Classe wrapper per gestire la connessione al database MySQL.
    Implementa metodi per CRUD operations senza usare ORM.
    """

    def __init__(self):
        """Inizializza il wrapper del database con le credenziali da .env"""
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.connection = None

    def connect(self):
        """
        Establishes a connection to the MySQL database.
        
        Returns:
            pymysql.connections.Connection: La connessione al database
            
        Raises:
            Exception: Se la connessione fallisce
        """
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            print(f"✓ Connessione al database '{self.database}' riuscita")
            return self.connection
        except pymysql.Error as e:
            print(f"✗ Errore connessione database: {e}")
            raise

    def close(self):
        """Chiude la connessione al database"""
        if self.connection:
            self.connection.close()
            print("✓ Connessione al database chiusa")

    def execute_query(self, query, params=None):
        """
        Esegue una query SELECT e ritorna i risultati.
        
        Args:
            query (str): La query SQL da eseguire
            params (tuple): I parametri da passare alla query (usando %s come placeholder)
            
        Returns:
            list: Lista di dizionari con i risultati
            
        Raises:
            Exception: Se la query fallisce
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except pymysql.Error as e:
            print(f"✗ Errore durante SELECT: {e}")
            raise

    def execute_insert(self, query, params=None):
        """
        Esegue una query INSERT.
        
        Args:
            query (str): La query SQL INSERT da eseguire
            params (tuple): I parametri da passare alla query
            
        Returns:
            int: L'ID dell'ultima riga inserita
            
        Raises:
            Exception: Se l'insert fallisce
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.lastrowid
        except pymysql.Error as e:
            self.connection.rollback()
            print(f"✗ Errore durante INSERT: {e}")
            raise

    def execute_update(self, query, params=None):
        """
        Esegue una query UPDATE.
        
        Args:
            query (str): La query SQL UPDATE da eseguire
            params (tuple): I parametri da passare alla query
            
        Returns:
            int: Numero di righe modificate
            
        Raises:
            Exception: Se l'update fallisce
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.rowcount
        except pymysql.Error as e:
            self.connection.rollback()
            print(f"✗ Errore durante UPDATE: {e}")
            raise

    def execute_delete(self, query, params=None):
        """
        Esegue una query DELETE.
        
        Args:
            query (str): La query SQL DELETE da eseguire
            params (tuple): I parametri da passare alla query
            
        Returns:
            int: Numero di righe eliminate
            
        Raises:
            Exception: Se il delete fallisce
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params or ())
                self.connection.commit()
                return cursor.rowcount
        except pymysql.Error as e:
            self.connection.rollback()
            print(f"✗ Errore durante DELETE: {e}")
            raise

    def create_tables(self):
        """
        Crea le tabelle necessarie per l'applicazione se non esistono.
        Questo metodo contiene tutti i CREATE TABLE.
        """
        try:
            with self.connection.cursor() as cursor:
                # Tabella Studenti
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Tabella Voti
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS grades (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id INT NOT NULL,
                        subject VARCHAR(50) NOT NULL,
                        grade INT NOT NULL,
                        grade_date DATE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                    )
                """)

                self.connection.commit()
                print("✓ Tabelle create o verificate con successo")
        except pymysql.Error as e:
            print(f"✗ Errore durante creazione tabelle: {e}")
            raise
