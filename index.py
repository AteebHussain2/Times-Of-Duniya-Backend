from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from routes.apiRoute import apiRoute

from dotenv import load_dotenv


load_dotenv()


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(
    apiRoute, prefix="/api/posts", tags=["create-articles-with-ai-agents"]
)
