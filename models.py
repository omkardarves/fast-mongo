# models.py
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
    priority: Optional[int] = Field(default=None)  # Optional with a default value of None
    due_date: Optional[str] = Field(default=None)  # Optional with a default value of None
    completed_timestamp: Optional[datetime] = Field(default=None)  # Optional datetime field with a default value of None


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