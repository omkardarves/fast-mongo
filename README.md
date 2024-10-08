# FastAPI + MongoDB with Beanie

This project demonstrates how to build a FastAPI application with MongoDB using Beanie, an asynchronous Python ODM (Object Document Mapper). It includes automated database migrations to handle schema changes seamlessly.

## Project Structure

```
fastapi-mongodb-beanie/
├── migrations/
│   ├── __init__.py
│   ├── migration_001_add_priority_due_date.py
│   ├── migration_002_add_completed_timestamp.py
├── main.py
├── .env
├── .gitignore
├── migration_runner.py
└── models.py
```

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8+
- FastAPI
- Uvicorn
- Beanie
- Motor (AsyncIO driver for MongoDB)
- Pydantic

Install the necessary packages using pip:

```bash
pip install fastapi uvicorn beanie[odm] motor pydantic python-dotenv
```

## Setting Up the Application

### `models.py`

Define the data models and migration record.

```python
from pydantic import BaseModel, Field
from beanie import Document
from typing import Optional
from datetime import datetime

class MigrationRecord(Document):
    name: str
    applied_at: datetime

    class Settings:
        collection = "migrations"

class TodoBase(BaseModel):
    name: str
    description: str
    complete: bool
    priority: Optional[int] = Field(default=None)
    due_date: Optional[str] = Field(default=None)
    completed_timestamp: Optional[datetime] = Field(default=None)

class TodoInDB(TodoBase):
    id: str

class Todo(Document, TodoBase):
    class Settings:
        collection = "todo_collection"

class TaskBase(BaseModel):
    task_name: str
    task_description: Optional[str] = None
    is_completed: bool
    due_date: Optional[str] = None

class TaskInDB(TaskBase):
    id: str

class Task(Document, TaskBase):
    class Settings:
        collection = "task_collection"
```

### `main.py`

Set up FastAPI and include migration handling.

```python
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import List
from beanie import init_beanie
import motor.motor_asyncio
from models import Todo, TodoBase, TodoInDB, Task, TaskBase, TaskInDB
from migration_runner import run_migrations
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init()
    await run_migrations()
    yield

app = FastAPI(title="Fast Mongo with Beanie", lifespan=lifespan)

# Database setup
async def init():
    MONGODB_URL = os.getenv('MONGODB_URL', '')
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
    database = client.fast_test_beanie
    await init_beanie(database, document_models=[Todo, Task, MigrationRecord])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    swagger_url = str(request.base_url) + "docs"
    return f'<a href="{swagger_url}">Swagger UI</a>'

@app.get("/todo/", tags=["Todo"], response_model=List[TodoInDB])
async def get_todos():
    todos = await Todo.find_all().to_list()
    return [todo.model_dump() | {"id": str(todo.id)} for todo in todos]

@app.post("/todo/", tags=["Todo"], response_model=TodoInDB)
async def post_todos(todo: TodoBase):
    todo_doc = Todo(**todo.dict())
    await todo_doc.insert()
    return todo_doc.model_dump() | {"id": str(todo_doc.id)}

@app.put("/todo/{id}", tags=["Todo"], response_model=TodoInDB)
async def put_todos(id: str, todo: TodoBase):
    todo_doc = await Todo.get(id)
    if todo_doc is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    update_data = todo.dict(exclude_unset=True)
    await todo_doc.update({"$set": update_data})
    return todo_doc.model_dump() | {"id": str(todo_doc.id)}

@app.delete("/todo/{id}", tags=["Todo"], response_model=TodoInDB)
async def delete_todos(id: str):
    todo_doc = await Todo.get(id)
    if todo_doc is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    await todo_doc.delete()
    return todo_doc.model_dump() | {"id": str(todo_doc.id)}

@app.get("/task/", tags=["Task"], response_model=List[TaskInDB])
async def get_tasks():
    tasks = await Task.find_all().to_list()
    return [task.model_dump() | {"id": str(task.id)} for task in tasks]

@app.post("/task/", tags=["Task"], response_model=TaskInDB)
async def post_tasks(task: TaskBase):
    task_doc = Task(**task.dict())
    await task_doc.insert()
    return task_doc.model_dump() | {"id": str(task_doc.id)}

@app.put("/task/{id}", tags=["Task"], response_model=TaskInDB)
async def put_tasks(id: str, task: TaskBase):
    task_doc = await Task.get(id)
    if task_doc is None:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task.dict(exclude_unset=True)
    await task_doc.update({"$set": update_data})
    return task_doc.model_dump() | {"id": str(task_doc.id)}

@app.delete("/task/{id}", tags=["Task"], response_model=TaskInDB)
async def delete_tasks(id: str):
    task_doc = await Task.get(id)
    if task_doc is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await task_doc.delete()
    return task_doc.model_dump() | {"id": str(task_doc.id)}
```

### `migration_runner.py`

Automate the migration process.

```python
import importlib
import os
from models import MigrationRecord
from datetime import datetime

# Directory where migration scripts are stored
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")

async def run_migrations():
    migration_files = sorted(f for f in os.listdir(MIGRATIONS_DIR) if f.startswith("migration_") and f.endswith(".py"))

    for migration_file in migration_files:
        migration_name = migration_file.split('.')[0]
        
        # Check if migration has already been applied
        existing_migration = await MigrationRecord.find_one({"name": migration_name})
        if existing_migration:
            print(f"Migration {migration_name} already applied.")
            continue
        
        # Import and run the migration
        try:
            module_name = f"migrations.{migration_name}"
            module = importlib.import_module(module_name)
            await module.migrate()
        except AttributeError as e:
            print(f"Migration {migration_name} does not have a 'migrate' function. Error: {e}")
            continue
        except ModuleNotFoundError as e:
            print(f"Migration file {migration_name} not found. Error: {e}")
            continue
        
        # Record the migration
        migration_record = MigrationRecord(name=migration_name, applied_at=datetime.utcnow())
        await migration_record.insert()

        print(f"Migration {migration_name} applied successfully.")
```

### Migration Files

#### `migration_001_add_priority_due_date.py`

Add `priority` and `due_date` fields to existing documents.

```python
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
```

#### `migration_002_add_completed_timestamp.py`

Add `completed_timestamp` to existing documents.

```python
from models import Todo
from datetime import datetime

async def migrate():
    async for todo in Todo.find_all():
        if 'completed_timestamp' not in todo:
            await todo.update({"$set": {"completed_timestamp": datetime.utcnow()}})
    print("Migration 002: add_completed_timestamp applied successfully.")
```

## Running the Application

To start your FastAPI application and apply any pending migrations, run:

```bash
uvicorn main:app --reload
```

## Conclusion

This guide demonstrates how to set up a FastAPI application with MongoDB using Beanie and manage schema changes with automated migrations. By following these steps, you can efficiently handle database updates while maintaining a scalable and robust application.
