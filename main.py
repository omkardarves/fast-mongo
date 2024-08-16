# main.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import List
from beanie import init_beanie
import motor.motor_asyncio
from migration_runner import run_migrations
from models import MigrationRecord, Todo, TodoBase, TodoInDB, Task, TaskBase, TaskInDB
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv(".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init()
    await run_migrations()
    yield

app = FastAPI(title="Fast Mongo with Beanie",lifespan=lifespan)

# Database setup
async def init():
    db_url = os.getenv('db_url','')
    client = motor.motor_asyncio.AsyncIOMotorClient(db_url)
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
    # Convert the model fields to a dict, but exclude '_id'
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

@app.get("/task/", tags = ["Task"], response_model=List[TaskInDB])
async def get_tasks():
    tasks = await Task.find_all().to_list()
    return [task.model_dump() | {"id": str(task.id)} for task in tasks]

@app.post("/task/", tags = ["Task"], response_model=TaskInDB)
async def post_tasks(task: TaskBase):
    task_doc = Task(**task.dict())
    await task_doc.insert()
    return task_doc.model_dump() | {"id": str(task_doc.id)}

@app.put("/task/{id}", tags = ["Task"], response_model=TaskInDB)
async def put_tasks(id: str, task: TaskBase):
    task_doc = await Task.get(id)
    if task_doc is None:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task.dict(exclude_unset=True)
    await task_doc.update({"$set": update_data})
    return task_doc.model_dump() | {"id": str(task_doc.id)}

@app.delete("/task/{id}", tags = ["Task"], response_model=TaskInDB)
async def delete_tasks(id: str):
    task_doc = await Task.get(id)
    if task_doc is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await task_doc.delete()
    return task_doc.model_dump() | {"id": str(task_doc.id)}