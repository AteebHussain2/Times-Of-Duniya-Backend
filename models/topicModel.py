from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class ExcludedTitles(BaseModel):
    international: List[str]
    anime: List[str]
    pakistan: List[str]
    politics: List[str]
    business: List[str]
    technology: List[str]
    sports: List[str]
    entertainment: List[str]
    health: List[str]
    blog: List[str]


class Category(BaseModel):
    id: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None
    name: str
    slug: str
    description: Optional[str] = None


class TopicModel(BaseModel):
    min_topics: int | None = 1
    max_topics: int | None = 2
    time_duration: str | None = "24 hours"
    excluded_titles: ExcludedTitles | None = []

class RetryTopicModel(BaseModel):
    min_topics: int | None = 1
    max_topics: int | None = 2
    time_duration: str | None = "24 hours"
    excluded_titles: List[str] | None = []
    categoryName: str
    categoryId: int
    jobId: int