# models.py
from pydantic import BaseModel
from beanie import Document


class TodoBase(BaseModel):
    name: str
    description: str
    complete: bool

class TodoInDB(TodoBase):
    id: str

class Todo(Document, TodoBase):
    class Settings:
        collection = "todo_collection"