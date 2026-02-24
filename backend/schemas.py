# backend/schemas.py

from pydantic import BaseModel


class Point(BaseModel):
    x: float
    y: float


class ScoreRequest(BaseModel):
    character: str = "5"
    user_points: list[Point]


class ScoreResponse(BaseModel):
    score: float
    character: str
    num_user_points: int
    feedback: str


class ReferenceResponse(BaseModel):
    character: str
    edge_points: list[Point]
    num_points: int
