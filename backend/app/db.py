import psycopg
from psycopg.rows import dict_row
from pgvector.psycopg import register_vector  # ← NEU
from .config import settings

def get_conn():
    conn = psycopg.connect(settings.database_url, row_factory=dict_row)
    register_vector(conn)  # ← WICHTIG: Adapter registrieren
    return conn
