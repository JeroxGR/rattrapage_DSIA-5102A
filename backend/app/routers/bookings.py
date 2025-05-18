from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from .. import schemas, models, database
from jose import JWTError, jwt
import os

router = APIRouter(prefix="/bookings", tags=["bookings"])

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
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/", response_model=schemas.BookingOut)
async def create_booking(
    booking: schemas.BookingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking); db.commit(); db.refresh(db_booking)
    return db_booking

@router.get("/", response_model=list[schemas.BookingOut])
async def list_bookings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Booking).all()

@router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_booking = db.query(models.Booking).get(booking_id)
    if not db_booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found")
    db.delete(db_booking); db.commit()
    return {"detail": "deleted"}