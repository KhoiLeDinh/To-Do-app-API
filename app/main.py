from fastapi import FastAPI
from app.core.security import encrypt_text, decrypt_text
from app.models.todo import ToDo
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from typing import Optional

app = FastAPI()

