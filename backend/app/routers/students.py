from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from .. import schemas, models, database
from jose import JWTError, jwt
import os

router = APIRouter(prefix="/students", tags=["students"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Validate JWT
def get_current_user(authorization: str = Header(...)) -> models.User:
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")
    db = database.SessionLocal()
    user = db.query(models.User).filter(models.User.username == username).first()
    db.close()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/", response_model=schemas.StudentOut)
async def create_student(
    student: schemas.StudentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_student = models.Student(**student.dict())
    db.add(db_student); db.commit(); db.refresh(db_student)
    return db_student

@router.get("/", response_model=list[schemas.StudentOut])
async def list_students(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Student).all()

@router.put("/{student_id}", response_model=schemas.StudentOut)
async def update_student(
    student_id: int,
    student: schemas.StudentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_student = db.query(models.Student).get(student_id)
    if not db_student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Student not found")
    for k, v in student.dict().items(): setattr(db_student, k, v)
    db.commit(); db.refresh(db_student)
    return db_student

@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_student = db.query(models.Student).get(student_id)
    if not db_student:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Student not found")
    db.delete(db_student); db.commit()
    return {"detail": "deleted"}