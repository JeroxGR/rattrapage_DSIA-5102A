from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str

class BookCreate(BookBase):
    pass

class BookOut(BookBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StudentBase(BaseModel):
    name: str
    email: str

class StudentCreate(StudentBase):
    pass

class StudentOut(StudentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookingBase(BaseModel):
    book_id: int
    student_id: int

class BookingCreate(BookingBase):
    pass

class BookingOut(BookingBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)