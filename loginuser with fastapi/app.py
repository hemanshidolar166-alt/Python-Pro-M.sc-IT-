from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import hashlib
import secrets
from pathlib import Path

# DATABASE

engine = create_engine(
    "sqlite:///./login.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


# USER TABLE

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    token = Column(String, nullable=True)


Base.metadata.create_all(engine)


# PASSWORD

def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# DEFAULT USER

db = SessionLocal()

user = db.query(User).filter(
    User.username == "admin"
).first()

if user is None:
    user = User(
        username="admin",
        password=hash_password("1234")
    )

    db.add(user)
    db.commit()

db.close()


# FASTAPI

app = FastAPI()


# LOGIN PAGE

@app.get("/", response_class=HTMLResponse)
def login_page():

    file_path = Path(__file__).parent / "login.html"

    return file_path.read_text(encoding="utf-8")


# LOGIN

@app.post("/login")
async def login(request: Request):

    data = await request.json()

    username = data.get("username")
    password = data.get("password")

    db = SessionLocal()

    user = db.query(User).filter(
        User.username == username
    ).first()

    if user is None:
        db.close()

        return {
            "success": False,
            "message": "Invalid username or password"
        }

    if user.password != hash_password(password):
        db.close()

        return {
            "success": False,
            "message": "Invalid username or password"
        }

    token = secrets.token_hex(32)

    user.token = token

    db.commit()
    db.close()

    response = RedirectResponse(
        "/home",
        status_code=303
    )

    response.set_cookie(
        "login_token",
        token,
        httponly=True
    )

    return response


# HOME

@app.get("/home", response_class=HTMLResponse)
def home(request: Request):

    token = request.cookies.get("login_token")

    if not token:
        return RedirectResponse(
            "/",
            status_code=303
        )

    db = SessionLocal()

    user = db.query(User).filter(
        User.token == token
    ).first()

    db.close()

    if user is None:
        return RedirectResponse(
            "/",
            status_code=303
        )


    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Home</title>

        <style>

            * {{
                box-sizing: border-box;
            }}

            body {{

                margin: 0;

                font-family: Arial, sans-serif;

                min-height: 100vh;

                background-image:
                    linear-gradient(
                        rgba(0,0,0,0.55),
                        rgba(0,0,0,0.55)
                    ),
                    url("https://images.unsplash.com/photo-1497366754035-f200968a6e72");

                background-size: cover;

                background-position: center;

                display: flex;

                justify-content: center;

                align-items: center;
            }}


            .home-box {{

                width: 500px;

                padding: 45px;

                text-align: center;

                background: rgba(
                    255,
                    255,
                    255,
                    0.95
                );

                border-radius: 20px;

                box-shadow:
                    0 20px 50px
                    rgba(0,0,0,0.4);
            }}


            .icon {{

                width: 80px;

                height: 80px;

                margin: auto;

                display: flex;

                justify-content: center;

                align-items: center;

                background: #667eea;

                color: white;

                border-radius: 50%;

                font-size: 38px;
            }}


            h1 {{

                margin-top: 25px;

                color: #222;

                font-size: 30px;
            }}


            .welcome {{

                color: #667eea;

                font-size: 18px;

                font-weight: bold;
            }}


            .description {{

                color: #777;

                margin-top: 15px;

                line-height: 1.6;
            }}


            .logout {{

                display: inline-block;

                margin-top: 25px;

                padding: 12px 30px;

                background: #e74c3c;

                color: white;

                text-decoration: none;

                border-radius: 8px;

                font-weight: bold;

                transition: 0.3s;
            }}


            .logout:hover {{

                background: #c0392b;

                transform: translateY(-2px);
            }}

        </style>

    </head>


    <body>


        <div class="home-box">

            <div class="icon">
                ✓
            </div>


            <h1>
                Welcome!
            </h1>


            <div class="welcome">
                Hello, {user.username}
            </div>


            <p class="description">

                You have successfully logged in.

                <br>

                You are authorized to access
                this application.

            </p>


            <a
                href="/logout"
                class="logout"
            >
                Logout
            </a>

        </div>


    </body>

    </html>
    """


# LOGOUT

@app.get("/logout")
def logout(request: Request):

    token = request.cookies.get("login_token")

    db = SessionLocal()

    user = db.query(User).filter(
        User.token == token
    ).first()

    if user:
        user.token = None
        db.commit()

    db.close()

    response = RedirectResponse(
        "/",
        status_code=303
    )

    response.delete_cookie("login_token")

    return response