from pydantic import BaseModel, EmailStr, ConfigDict

# Pydantic schemas for user registration, login, and profile responses,
# including email validation and JWT authentication tokens.

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"