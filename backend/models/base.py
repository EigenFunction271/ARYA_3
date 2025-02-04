from pydantic import BaseModel

class User(BaseModel):
    username: str
    hashed_password: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Query(BaseModel):
    query: str 