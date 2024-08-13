# main.py
from fastapi import FastAPI, HTTPException
from typing import List
from pymongo import ReturnDocument

app = FastAPI(title="Fast Mongo")

from models import Todo, TodoInDB
from database import collection_name
from schema import list_serial, single_serial
from bson import ObjectId

@app.get("/", response_model=List[TodoInDB])
async def get_todos():
    todos = collection_name.find()
    return list_serial(todos)

@app.post("/", response_model=TodoInDB)
async def post_todos(todo: Todo):
    result = collection_name.insert_one(todo.dict())
    return {"id": str(result.inserted_id), **todo.dict()}

@app.put("/{id}", response_model=TodoInDB)
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

@app.delete("/{id}", response_model=TodoInDB)
async def delete_todos(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID format")
    result = collection_name.find_one_and_delete({"_id": ObjectId(id)})
    if result is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return single_serial(result)