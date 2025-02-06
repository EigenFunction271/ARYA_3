from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserCreate):
    role: UserRole = UserRole.USER
    disabled: bool = False 