# migration_001_add_priority_due_date.py
from models import Todo

async def migrate():
    async for todo in Todo.find_all():
        update_data = {}
        if 'priority' not in todo:
            update_data['priority'] = 0
        if 'due_date' not in todo:
            update_data['due_date'] = ''
        
        if update_data:
            await todo.update({"$set": update_data})
    print("Migration 001: add_priority_due_date applied successfully.")
