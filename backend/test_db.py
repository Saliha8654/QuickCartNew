from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

dburl = os.getenv("DATABASE_URL")
print("Using DB URL:", dburl)

engine = create_engine(dburl)

with engine.connect() as conn:
    r = conn.execute(text("SELECT 1"))
    print("DB Test OK, result:", r.scalar())
