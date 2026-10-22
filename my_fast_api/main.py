
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Boolean, DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker
from starlette.middleware.sessions import SessionMiddleware


# 1. DATABASE SETUP

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{(BASE_DIR / 'tasks.db').as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# 2. TASK TABLE

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(300), default="")
    priority = Column(String(20), default="Medium")
    is_completed = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# 3. CREATE TABLE AUTOMATICALLY

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Personal Task Tracker",
    version="1.0.0",
    lifespan=lifespan
)

# Change this secret before deployment.
app.add_middleware(
    SessionMiddleware,
    secret_key="change-this-to-a-long-random-secret-key"
)


# 4. INPUT DATA MODELS

class LoginData(BaseModel):
    username: str = Field(min_length=1, max_length=100)


class TaskData(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=300)
    priority: str = "Medium"


# 5. CHECK LOGIN

def get_username(request: Request):
    username = request.session.get("username")

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Please login first using POST /login"
        )

    return username


# 6. CHECK TASK OWNER

def get_task(db, task_id, username):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.created_by == username
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


# 7. VALIDATE TASK DATA

def validate_task(data: TaskData):
    title = data.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    if data.priority not in ["High", "Medium", "Low"]:
        raise HTTPException(
            status_code=400,
            detail="Priority must be High, Medium or Low"
        )

    return title


# 8. LOGIN PAGE INFORMATION
# Without HTML, GET /login returns JSON instructions.

@app.get("/login")
def login_page():
    return {
        "message": "Login using POST /login",
        "example": {
            "username": "Hasmukh"
        }
    }


# 9. LOGIN
# Store username in the session.

@app.post("/login")
def login(data: LoginData, request: Request):
    username = data.username.strip()

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Please enter your name"
        )

    request.session.clear()
    request.session["username"] = username

    return {
        "message": "Login successful",
        "username": username
    }


# 10. HOME
# Show pending and completed tasks separately.

@app.get("/")
def home(request: Request):
    username = get_username(request)
    db = SessionLocal()

    try:
        tasks = db.query(Task).filter(
            Task.created_by == username
        ).order_by(Task.created_at.desc()).all()

        pending = []
        completed = []

        for task in tasks:
            if task.is_completed:
                completed.append(task)
            else:
                pending.append(task)

        return {
            "username": username,
            "pending_tasks": pending,
            "completed_tasks": completed
        }
    finally:
        db.close()


# 11. ADD TASK

@app.post("/add")
def add_task(data: TaskData, request: Request):
    username = get_username(request)
    title = validate_task(data)

    db = SessionLocal()

    try:
        task = Task(
            title=title,
            description=data.description.strip(),
            priority=data.priority,
            is_completed=False,
            created_by=username,
            created_at=datetime.now()
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "message": "Task added successfully",
            "task": task
        }
    finally:
        db.close()


# 12. TOGGLE TASK STATUS

@app.get("/toggle/{id}")
def toggle_task(id: int, request: Request):
    username = get_username(request)
    db = SessionLocal()

    try:
        task = get_task(db, id, username)

        task.is_completed = not task.is_completed

        db.commit()
        db.refresh(task)

        return {
            "message": "Task status changed",
            "task": task
        }
    finally:
        db.close()


# 13. GET TASK DETAILS FOR EDITING

@app.get("/edit/{id}")
def edit_task(id: int, request: Request):
    username = get_username(request)
    db = SessionLocal()

    try:
        task = get_task(db, id, username)

        return {
            "message": "Task details",
            "task": task
        }
    finally:
        db.close()


# 14. UPDATE TASK

@app.post("/update/{id}")
def update_task(
    id: int,
    data: TaskData,
    request: Request
):
    username = get_username(request)
    title = validate_task(data)

    db = SessionLocal()

    try:
        task = get_task(db, id, username)

        task.title = title
        task.description = data.description.strip()
        task.priority = data.priority

        db.commit()
        db.refresh(task)

        return {
            "message": "Task updated successfully",
            "task": task
        }
    finally:
        db.close()


# 15. DELETE TASK

@app.post("/delete/{id}")
def delete_task(id: int, request: Request):
    username = get_username(request)
    db = SessionLocal()

    try:
        task = get_task(db, id, username)

        db.delete(task)
        db.commit()

        return {
            "message": "Task deleted successfully",
            "task_id": id
        }
    finally:
        db.close()


# 16. SET THEME COOKIE

@app.get("/set-theme/{theme}")
def set_theme(theme: str, request: Request):
    get_username(request)

    if theme not in ["light", "dark"]:
        raise HTTPException(
            status_code=400,
            detail="Theme must be light or dark"
        )

    response = JSONResponse({
        "message": "Theme saved successfully",
        "theme": theme
    })

    response.set_cookie(
        key="theme",
        value=theme,
        max_age=31536000,
        httponly=True,
        samesite="lax"
    )

    return response


# 17. LOGOUT

@app.get("/logout")
def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logout successful"
    }
