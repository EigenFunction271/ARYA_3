import json
import os
from pathlib import Path
from typing import Optional
from passlib.context import CryptContext
from models.user import UserInDB, UserCreate, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager:
    def __init__(self):
        self.users_file = Path("data/users.json")
        self.users_file.parent.mkdir(exist_ok=True)
        if not self.users_file.exists():
            # Create default admin user
            self.users = {
                "admin@example.com": UserInDB(
                    email="admin@example.com",
                    password=pwd_context.hash("adminpassword"),
                    role=UserRole.ADMIN
                ).dict()
            }
            self.save_users()
        else:
            with open(self.users_file) as f:
                self.users = json.load(f)

    def save_users(self):
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=4)

    def get_user(self, email: str) -> Optional[UserInDB]:
        if email not in self.users:
            return None
        return UserInDB(**self.users[email])

    def create_user(self, user: UserCreate) -> UserInDB:
        if user.email in self.users:
            raise ValueError("Email already registered")
        
        db_user = UserInDB(
            email=user.email,
            password=pwd_context.hash(user.password)
        )
        self.users[user.email] = db_user.dict()
        self.save_users()
        return db_user

    def set_user_role(self, email: str, role: UserRole) -> Optional[UserInDB]:
        if email not in self.users:
            return None
        self.users[email]["role"] = role
        self.save_users()
        return UserInDB(**self.users[email])

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password) 