# models.py
from pydantic import BaseModel

class Todo(BaseModel):
    name: str
    description: str
    complete: bool

class TodoInDB(Todo):
    id: str
