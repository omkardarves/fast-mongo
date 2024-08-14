# migration_002_add_completed_timestamp.py
from models import Todo
from datetime import datetime

async def migrate():
    async for todo in Todo.find_all():
        if 'completed_timestamp' not in todo:
            await todo.update({"$set": {"completed_timestamp": datetime.utcnow()}})
    print("Migration 002: add_completed_timestamp applied successfully.")
