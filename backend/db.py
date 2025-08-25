import psycopg
from psycopg.rows import dict_row
from .config import settings

def get_conn():
    """
    Liefert eine neue DB-Verbindung.
    DATABASE_URL sollte sslmode=require enthalten.
    """
    return psycopg.connect(settings.database_url, row_factory=dict_row)
