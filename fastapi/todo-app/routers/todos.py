import sys
sys.path.append('..')

from fastapi import FastAPI, Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from . import auth


# app = FastAPI()
router = APIRouter(
    prefix='/todos',
    tags=['todos'],
    responses={404: {'user': 'Todos not found'}}
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description='Pririty must be between 1-5')
    complete: bool



@router.get('/all')
async def read_all_no_auth(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@router.get('/')
async def read_all(user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db.query(models.Todos).all()


@router.get('/user/{user_id}')
async def read_all_by_user(user: dict = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise HTTPException(status_code=404, detail='User not found')
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get('id')).all()

@router.get('/todo/{todo_id}')
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    if todo_model is not None:
        return todo_model
    raise http_exception()


@router.post('/')
async def create_todo(todo: Todo, db: Session = Depends(get_db)):
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return {
        'status_code': 201,
        'transaction': 'Successful'
    }

@router.put('/{todo_id}')
async def update_todo(todo_id: int, todo: Todo, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is None:
        raise http_exception()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return {
        'status_code': 200,
        'transaction': 'Updated Succesfuly'
    }


@router.delete('/{todo_id}')
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo_model is None:
        raise  http_exception()

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()
    return {
        'status': 200,
        'transaction': 'Succesfull'
    }


def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")