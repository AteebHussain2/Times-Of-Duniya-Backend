from pydantic import BaseModel

class ArticleModel(BaseModel):
    title: str
    summary: str
    published: str
    sources: str
    categoryId: int
    jobId: int
    trigger: str
    topicId: int
