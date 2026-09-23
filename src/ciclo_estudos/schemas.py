from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Message(BaseModel):
    message: str


class SubjectSchema(BaseModel):
    name: str = Field(min_length=1)
    target_hours: float = Field(gt=0)


class SubjectPublic(BaseModel):
    id: int
    name: str
    target_hours: float
    completed_hours: float
    model_config = ConfigDict(from_attributes=True)


class SubjectList(BaseModel):
    subjects: list[SubjectPublic]


class UserSchema(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class FilterPage(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=100, gt=0, le=100)
