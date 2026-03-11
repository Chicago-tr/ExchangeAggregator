import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
db_url = os.getenv("DB_URL")
if not db_url:
    raise ValueError("No DB_URL in .env")

engine = create_engine(db_url)
