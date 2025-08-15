from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from lib.validate_key import isValidApiKey
from fastapi import APIRouter, Header
import json
import os

# Queue for AI Agents
# Redis Imports for queue management
from redis import Redis
from rq import Queue

# Create Topics with AI Agents
from config.topic.create_topics import run_researcher_crew
from schemas.topicSchema import TopicEntity
from models.topicModel import TopicModel

# Create Articles with AI Agents using Topics
from config.article.create_article import run_article_writer_crew
from schemas.articleSchema import ArticleEntity
from models.articleModel import ArticleModel

REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise ValueError("REDIS_URL environment variable is not set")

apiRoute = APIRouter()
redis_conn = Redis.from_url(
    REDIS_URL
    or "redis://default:EisIgbzSIOUOtaAHHLaqCWVSgRiNEwTk@gondola.proxy.rlwy.net:56125"
)
task_queue = Queue(connection=redis_conn)


@apiRoute.post("/create-topics")
async def create_topics(
    authorization: str = Header(None),
    body: TopicModel = None,
):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

    secret = authorization.split(" ")[1]
    if not isValidApiKey(secret):
        return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

    try:
        data = TopicEntity(body)
        category_json = jsonable_encoder(data["category"])
        task_queue.enqueue(
            run_researcher_crew,
            args=(
                data["min_topics"],
                data["max_topics"],
                data["time_duration"],
                data["excluded_titles"],
                category_json["name"],
                category_json["id"],
                data["trigger"],
                data["jobId"],
            ),
            job_timeout=60 * 15,
        )

        return JSONResponse(
            content={
                "message": "Successfully added process to queue",
            },
            status_code=200,
        )

    except Exception as e:
        print(json.dumps(e, indent=4))
        return JSONResponse(
            content={"message": "Invalid request body"}, status_code=400
        )


@apiRoute.post("/create-article")
async def create_article(authorization: str = Header(None), body: ArticleModel = None):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

    secret = authorization.split(" ")[1]
    if not isValidApiKey(secret):
        return JSONResponse(content={"message": "Unauthorized"}, status_code=401)

    if not body:
        return JSONResponse(
            content={"message": "Invalid request body"}, status_code=400
        )

    try:
        data = ArticleEntity(body)
        task_queue.enqueue(
            run_article_writer_crew,
            args=(
                data["title"],
                data["summary"],
                data["sources"],
                data["jobId"],
                data["categoryId"],
                data["trigger"],
                data["topicId"],
            ),
            job_timeout=60 * 15,
        )

        return JSONResponse(
            content={
                "message": "Successfully added process to queue",
            },
            status_code=200,
        )

    except Exception as e:
        print("@@ERROR:", e)
        return JSONResponse(
            content={"message": "Invalid request body"}, status_code=400
        )
