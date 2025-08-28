```python
import logging
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from .models import get_db, create_note, get_note, update_note, delete_note, create_user, User, Note, AsyncSession
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Note Taking App", description="A simple note taking application", version="1.0.0")

origins = ["*"]  # Update with your allowed origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    user_id: int = Field(...)

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)

@app.get("/health", response_model=str)
async def health_check():
    return "OK"

@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_user(db, user.username)
    except IntegrityError as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")


@app.post("/notes", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note_endpoint(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_note(db, note.title, note.content, note.user_id)
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating note")

@app.get("/notes/{note_id}", response_model=Note)
async def get_note_endpoint(note_id: int, db: AsyncSession = Depends(get_db)):
    note = await get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=Note)
async def update_note_endpoint(note_id: int, note_update: NoteUpdate, db: AsyncSession = Depends(get_db)):
    updated_note = await update_note(db, note_id, note_update.title, note_update.content)
    if not updated_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return updated_note

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_endpoint(note_id: int, db: AsyncSession = Depends(get_db)):
    if not await delete_note(db, note_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

#Example usage with uvicorn
# uvicorn generated_projects.web_app_1756222726.main:app --reload
```