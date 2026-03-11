import pymysql
from config import DB_CONFIG

def get_db_connection():
    """Crea i retorna una conexió a la base de dades"""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor
    )

def execute_query(query, params=None, fetch=True):
    """Executa una query i retorna els resultats"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
    finally:
        conn.close()

def execute_single(query, params=None):
    """Executa una query i retorna un únic resultat"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        conn.close()
