from pydantic import BaseModel, ConfigDict, Field


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
