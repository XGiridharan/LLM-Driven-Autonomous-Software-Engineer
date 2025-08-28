from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
import jwt
from datetime import datetime, timedelta

app = FastAPI()
engine = create_engine("sqlite:///blog.db")
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(Text)
    author_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

@app.post("/register")
async def register(username: str, email: str, password: str):
    # Registration logic
    pass

@app.post("/login")
async def login(username: str, password: str):
    # Login logic
    pass

@app.post("/posts")
async def create_post(title: str, content: str):
    # Create post logic
    pass

@app.get("/posts")
async def get_posts():
    # Get posts logic
    pass