from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class Message(BaseModel):
    message: str


class SubjectSchema(BaseModel):
    name: str = Field(min_length=1)
    target_hours: float = Field(gt=0)


class SubjectPublic(BaseModel):
    id: int
    name: str
    target_hours: float
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


class UTCModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_validator('*')
    @classmethod
    def ensure_utc(cls, value):
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class StudySessionSchema(BaseModel):
    subject_id: int
    minutes: int = Field(gt=0, le=600)
    notes: str | None = Field(default=None, max_length=280)


class StudySessionPublic(UTCModel):
    id: int
    subject_id: int
    cycle_id: int
    minutes: int
    notes: str | None
    studied_at: datetime


class StudySessionList(BaseModel):
    sessions: list[StudySessionPublic]


class SubjectProgressPublic(BaseModel):
    id: int
    name: str
    target_hours: float
    completed_hours: float
    is_complete: bool
    model_config = ConfigDict(from_attributes=True)


class CycleProgressPublic(UTCModel):
    id: int
    number: int
    started_at: datetime
    total_target_hours: float
    total_completed_hours: float
    is_complete: bool
    subjects: list[SubjectProgressPublic]


class CyclePublic(UTCModel):
    id: int
    number: int
    started_at: datetime
    finished_at: datetime | None
