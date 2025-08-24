from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from lib.validate_key import isValidApiKey
from fastapi import APIRouter, Header, FastAPI
from contextlib import asynccontextmanager

from prisma import Prisma
from prisma.enums import TYPE, TRIGGER, STATUS
import json
import os

# Queue for AI Agents
from redis import Redis
from rq import Queue

# Create Topics with AI Agents
from config.topic.create_topics import run_researcher_crew
from schemas.topicSchema import TopicEntity, RetryTopicEntity
from models.topicModel import TopicModel, RetryTopicModel

# Create Articles with AI Agents using Topics
from config.article.create_article import run_article_writer_crew
from schemas.articleSchema import ArticleEntity
from models.articleModel import ArticleModel


db = Prisma()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup block
    await db.connect()
    yield
    # Shutdown block
    await db.disconnect()


apiRoute = APIRouter(lifespan=lifespan)

redis_conn = Redis(host="localhost", port=6379, db=0)
task_queue = Queue(connection=redis_conn)


@apiRoute.post("/cron/create-topics")
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
        excluded_titles_json = jsonable_encoder(data["excluded_titles"])
        categories = await db.category.find_many(where={"slug": {"not": "blog"}})

        for category in categories:
            job = await db.job.create(
                data={
                    "categoryId": category.id,
                    "type": TYPE.TOPIC_GENERATION,
                    "trigger": TRIGGER.CRON,
                    "status": STATUS.QUEUED,
                },
            )

            task_queue.enqueue(
                run_researcher_crew,
                args=(
                    data["min_topics"],
                    data["max_topics"],
                    data["time_duration"],
                    excluded_titles_json[category.slug],
                    category.name,
                    category.id,
                    TRIGGER.CRON,
                    job.id,
                ),
            ),

        return JSONResponse(
            content={
                "message": "Successfully added process to queue",
            },
            status_code=200,
        )

    except Exception as e:
        print(e)
        return JSONResponse(
            content={"message": "Invalid request body"}, status_code=400
        )


@apiRoute.post("/create-topic/retry")
async def retry_topic(
    authorization: str = Header(None),
    body: RetryTopicModel = None,
):
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
        data = RetryTopicEntity(body)

        job = await db.job.find_unique(where={"id": data["jobId"]})
        if not job:
            return JSONResponse(content={"message": "Job not found"}, status_code=404)

        await db.job.update(
            where={"id": data["jobId"]},
            data={
                "status": STATUS.QUEUED,
                "error": "",
            },
        )

        task_queue.enqueue(
            run_researcher_crew,
            args=(
                data["min_topics"],
                data["max_topics"],
                data["time_duration"],
                data["excluded_titles"],
                data["categoryName"],
                data["categoryId"],
                job.trigger,
                data["jobId"],
            ),
            job_timeout=60 * 10,
        )

        return JSONResponse(
            content={"message": f"Retry job {data['jobId']} enqueued successfully"},
            status_code=200,
        )

    except Exception as e:
        print("@@ERROR (retry_topic):", e)
        return JSONResponse(content={"message": "Failed to retry job"}, status_code=400)


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

        await db.job.update(
            where={
                "id": data["jobId"],
            },
            data={
                "status": STATUS.QUEUED,
                "type": TYPE.ARTICLE_GENERATION,
            },
        )

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
