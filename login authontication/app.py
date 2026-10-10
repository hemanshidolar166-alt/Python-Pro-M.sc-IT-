from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import jwt


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="JWT Authentication System"
)


# =====================================================
# DATABASE
# =====================================================

DATABASE_URL = "sqlite:///./users.db"

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


# =====================================================
# USER TABLE
# =====================================================

class UserTable(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String,
        nullable=False
    )

    full_name = Column(
        String,
        nullable=False
    )


Base.metadata.create_all(bind=engine)


# =====================================================
# JWT
# =====================================================

SECRET_KEY = "my-super-secret-key-fastapi-jwt-2026"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)


# =====================================================
# PASSWORD HASH
# =====================================================

def hash_password(password: str):

    salt = secrets.token_hex(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    )

    return salt + ":" + hashed.hex()


def verify_password(
    password: str,
    stored_password: str
):

    try:

        salt, stored_hash = stored_password.split(":")

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        )

        return secrets.compare_digest(
            hashed.hex(),
            stored_hash
        )

    except Exception:

        return False


# =====================================================
# PYDANTIC MODEL
# =====================================================

class UserSignup(BaseModel):

    username: str

    password: str

    full_name: str


# =====================================================
# DATABASE SESSION
# =====================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "message": "API is running successfully"
    }


# =====================================================
# SIGNUP
# =====================================================

@app.post("/signup")
def signup(
    user: UserSignup,
    db: Session = Depends(get_db)
):

    # Check existing username
    existing_user = db.query(UserTable).filter(
        UserTable.username == user.username
    ).first()

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    # Hash password
    password_hash = hash_password(
        user.password
    )

    # Create user
    new_user = UserTable(
        username=user.username,
        password=password_hash,
        full_name=user.full_name
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "id": new_user.id,
        "username": new_user.username,
        "full_name": new_user.full_name
    }


# =====================================================
# LOGIN
# =====================================================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(UserTable).filter(
        UserTable.username == form_data.username
    ).first()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user.username,
        "name": user.full_name,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =====================================================
# CURRENT USER
# =====================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = db.query(UserTable).filter(
            UserTable.username == username
        ).first()

        if user is None:

            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:

        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )

    except jwt.InvalidTokenError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# =====================================================
# PROFILE
# =====================================================

@app.get("/profile")
def profile(
    current_user: UserTable = Depends(get_current_user)
):

    return {
        "message": "Authentication successful",
        "id": current_user.id,
        "username": current_user.username,
        "full_name": current_user.full_name
    }


# =====================================================
# GET ALL USERS
# =====================================================

@app.get("/users")
def get_users(
    db: Session = Depends(get_db)
):

    users = db.query(UserTable).all()

    return {
        "total_users": len(users),
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name
            }
            for user in users
        ]
    }


# =====================================================
# GET USER BY ID
# =====================================================

@app.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):

    user = db.query(UserTable).filter(
        UserTable.id == user_id
    ).first()

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name
    }