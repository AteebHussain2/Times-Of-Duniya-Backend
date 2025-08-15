from fastapi import FastAPI
from routes.apiRoute import apiRoute
from dotenv import load_dotenv


load_dotenv()


app = FastAPI()

app.include_router(
    apiRoute, prefix="/api/posts", tags=["create-articles-with-ai-agents"]
)
