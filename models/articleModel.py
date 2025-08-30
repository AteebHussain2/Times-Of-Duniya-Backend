from pydantic import BaseModel
from typing import List


class ArticleModel(BaseModel):
    title: str
    summary: str
    published: str
    sources: List[str] | str
    categoryId: int
    jobId: int
    trigger: str
    topicId: int


class ManualArticleModel(BaseModel):
    title: str
    summary: str
    published: str
    sources: List[str] | str
    categoryId: int
    jobId: int
    topicId: int
    userId: str
    trigger: str
    prompt: str
