from fastapi import FastAPI
from databases import Database
import sqlalchemy

DATABASE_URL = "sqlite:///./test.db"

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Example table
notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("text", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("completed", sqlalchemy.Boolean, default=False),
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def read_notes():
    query = notes.select()
    return await database.fetch_all(query)

@app.post("/")
async def create_note(text: str, completed: bool = False):
    query = notes.insert().values(text=text, completed=completed)
    last_record_id = await database.execute(query)
    return {"id": last_record_id, "text": text, "completed": completed}
