from fastapi import FastAPI, Form, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date

app = FastAPI()

# =========================
# DATABASE
# =========================

DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


# =========================
# MODEL
# =========================

class Todo(Base):

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)

    description = Column(String(300), nullable=True)

    priority = Column(String(20), nullable=False)

    is_completed = Column(Boolean, default=False)

    due_date = Column(Date, nullable=True)


Base.metadata.create_all(bind=engine)


# =========================
# GET /
# =========================

@app.get("/")
def get_tasks():

    db = SessionLocal()

    try:

        pending = db.query(Todo).filter(
            Todo.is_completed == False
        ).all()

        completed = db.query(Todo).filter(
            Todo.is_completed == True
        ).all()

        return {
            "pending_tasks": [
                {
                    "id": x.id,
                    "title": x.title,
                    "description": x.description,
                    "priority": x.priority,
                    "is_completed": x.is_completed,
                    "due_date": x.due_date
                }
                for x in pending
            ],

            "completed_tasks": [
                {
                    "id": x.id,
                    "title": x.title,
                    "description": x.description,
                    "priority": x.priority,
                    "is_completed": x.is_completed,
                    "due_date": x.due_date
                }
                for x in completed
            ]
        }

    finally:
        db.close()


# =========================
# POST /add
# =========================

@app.post("/add")
def add_task(
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form(...),
    due_date: date = Form(...)
):

    if priority not in ["High", "Medium", "Low"]:
        raise HTTPException(
            status_code=400,
            detail="Priority must be High, Medium or Low"
        )

    db = SessionLocal()

    try:

        task = Todo(
            title=title,
            description=description,
            priority=priority,
            is_completed=False,
            due_date=due_date
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return {
            "message": "Task added successfully",
            "id": task.id
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()


# =========================
# GET /toggle/{id}
# =========================

@app.get("/toggle/{id}")
def toggle_task(id: int):

    db = SessionLocal()

    try:

        task = db.query(Todo).filter(
            Todo.id == id
        ).first()

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        task.is_completed = not task.is_completed

        db.commit()

        return {
            "message": "Task status changed successfully",
            "id": task.id,
            "is_completed": task.is_completed
        }

    finally:
        db.close()


# =========================
# POST /update/{id}
# =========================

@app.post("/update/{id}")
def update_task(
    id: int,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form(...),
    due_date: date = Form(...)
):

    if priority not in ["High", "Medium", "Low"]:
        raise HTTPException(
            status_code=400,
            detail="Priority must be High, Medium or Low"
        )

    db = SessionLocal()

    try:

        # Find task
        task = db.query(Todo).filter(
            Todo.id == id
        ).first()

        # If ID doesn't exist
        if task is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {id} not found"
            )

        # Update values
        task.title = title
        task.description = description
        task.priority = priority
        task.due_date = due_date

        db.commit()
        db.refresh(task)

        return {
            "message": "Task updated successfully",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "is_completed": task.is_completed,
                "due_date": task.due_date
            }
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()


# =========================
# POST /delete/{id}
# =========================

@app.post("/delete/{id}")
def delete_task(id: int):

    db = SessionLocal()

    try:

        # Find task
        task = db.query(Todo).filter(
            Todo.id == id
        ).first()

        # ID not found
        if task is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with id {id} not found"
            )

        # Delete
        db.delete(task)

        # Save change
        db.commit()

        return {
            "message": "Task deleted successfully",
            "deleted_id": id
        }

    except HTTPException:
        raise

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()