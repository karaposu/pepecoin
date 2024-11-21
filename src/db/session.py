# db/session.py

from sqlalchemy import create_engine

def get_engine(db_url):
    return create_engine(db_url)