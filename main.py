from fastapi import FastAPI, HTTPException

app = FastAPI(title="Fast Mongo")

from models import Todo
from database import collection_name
from schema import list_serial
from bson import ObjectId

@app.get("/")
async def get_todos():
    return list_serial(collection_name.find())


@app.post("/")
async def post_todos(todo: Todo):
    result = collection_name.insert_one(dict(todo))
    return {"inserted_id": str(result.inserted_id)}


@app.put("/{id}")
async def put_todos(id: str, todo: Todo):
    result = collection_name.find_one_and_update({"_id": ObjectId(id)},{"$set": dict(todo)})
    return {"updated_id": str(result.get("_id"))}

@app.delete("/{id}")
async def delete_todos(id: str):
    result = collection_name.find_one_and_delete({"_id": ObjectId(id)})
    if not result:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"deleted_id": str(result.get("_id"))}



    