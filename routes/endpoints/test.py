from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import schemas
from db.session import SessionLocal

router = APIRouter()

# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



    # Routes
@router.get("/")
def return_test():

    return "hello";
