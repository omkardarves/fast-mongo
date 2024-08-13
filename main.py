# main.py
from fastapi import FastAPI, HTTPException, Request
from typing import List
from pymongo import ReturnDocument
from fastapi.responses import HTMLResponse

app = FastAPI(title="Fast Mongo")

from models import Todo, TodoInDB
from database import collection_name
from schema import list_serial, single_serial
from bson import ObjectId

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    swagger_url = str(request.base_url) + "docs"
    return f'<a href="{swagger_url}">Swagger UI</a>'

@app.get("/todo/", response_model=List[TodoInDB])
async def get_todos():
    todos = collection_name.find()
    return list_serial(todos)

@app.post("/todo/", response_model=TodoInDB)
async def post_todos(todo: Todo):
    result = collection_name.insert_one(todo.model_dump())
    return {"id": str(result.inserted_id), **todo.model_dump()}

@app.put("/todo/{id}", response_model=TodoInDB)
async def put_todos(id: str, todo: Todo):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = collection_name.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": todo.model_dump()},
        return_document=ReturnDocument.AFTER
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return single_serial(result)

@app.delete("/todo/{id}", response_model=TodoInDB)
async def delete_todos(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = collection_name.find_one_and_delete({"_id": ObjectId(id)})
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return single_serial(result)