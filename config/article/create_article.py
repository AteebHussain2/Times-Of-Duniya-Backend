from lib.clean_crewai_response import clean_crewai_article, clean_usage_tokens
from config.article.agents import ArticleWriterAgents
from config.article.tasks import ArticleWriterTasks
from config.manager.agents import ManagerAgents
from crewai import Crew, Process
from prisma.enums import STATUS, ARTICLESTATUS, TYPE
from prisma import Prisma
from typing import List
from lib.revalidate import revalidate
import asyncio
import os


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")


class ArticleWriterCrew:
    def __init__(self, title: str, summary: str, sources: List[str] | str):
        self.topic_title = title
        self.summary = summary
        self.sources = sources

    def run(self):
        # Defining custom agents and tasks in agents.py and tasks.py
        agents = ArticleWriterAgents()
        tasks = ArticleWriterTasks()

        # Custom Agents for writing articles
        informant = agents.informant()
        news_mentalist = agents.news_mentalist()
        final_editor = agents.final_editor()
        manager_agent = ManagerAgents().manager_agent()

        # Custom Tasks for writing articles
        research_task = tasks.gather_research_data(
            informant, self.topic_title, self.summary, self.sources
        )
        write_task = tasks.write_news_article(
            news_mentalist, self.topic_title, self.summary, [research_task]
        )
        review_task = tasks.editorial_review(
            final_editor,
            self.topic_title,
            self.sources,
            self.summary,
            [write_task],
        )

        NewsLetterCrew = Crew(
            agents=[informant, news_mentalist, final_editor],
            tasks=[research_task, write_task, review_task],
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager_agent,
            max_rpm=15,
            memory=True,
            embedder={
                "provider": "google",
                "config": {
                    "api_key": GOOGLE_API_KEY,
                    "model": "text-embedding-004",
                },
            },
        )

        res = NewsLetterCrew.kickoff()

        return res


async def run_article_writer_crew_async(
    title: str,
    summary: str,
    sources: List[str] | str,
    jobId: int,
    categoryId: int,
    trigger: str,
    topicId: int,
):
    SECRET_KEY = os.getenv("SECRET_KEY")
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")

    if not SECRET_KEY or not FRONTEND_BASE_URL:
        return "Environment varaibles not found for SECRET_KEY and FRONTEND_BASE_URL"

    DEFAULT_USAGE = {
        "date": "0000-00-00T00:00:00Z",
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "successful_requests": 0,
    }

    db = Prisma()
    await db.connect()

    await db.job.update(
        where={
            "id": jobId,
        },
        data={
            "status": STATUS.PROCESSING,
        },
    )

    revalidate(trigger, STATUS.PROCESSING, TYPE.ARTICLE_GENERATION)

    try:
        # Initialize the Crew with provided parameters
        crew = ArticleWriterCrew(
            title,
            summary,
            sources,
        )

        # Run the Crew to get topics
        res = crew.run()

        data = getattr(res, "json_dict", None) or str(res)
        raw_article = clean_crewai_article(data)

        metrics = getattr(res, "token_usage", None)
        usage_json = clean_usage_tokens(metrics) if metrics else DEFAULT_USAGE

        # Send topics to Next.js webhook if valid
        if raw_article and "article" in raw_article and raw_article["article"]:
            article = raw_article["article"]

            article_status = (
                ARTICLESTATUS.APPROVED
                if article
                and len(article.get("content", "")) > 0
                and article.get("status") == "APPROVED"
                else ARTICLESTATUS.REJECTED
            )

            await db.article.create(
                data={
                    "topicId": topicId,
                    "jobId": jobId,
                    "categoryId": categoryId,
                    "status": STATUS.COMPLETED,
                    "title": article.get("title"),
                    "summary": article.get("summary"),
                    "content": article.get("content"),
                    "tags": article.get("tags"),
                    "source": article.get("source"),
                    "articleStatus": article_status,
                    "accuracy": raw_article.get("accuracy_score"),
                    "reasoning": raw_article.get("reason"),
                    "feedback": raw_article.get("feedback"),
                }
            )

            print(f"✅ Article saved successfully!")

            await db.job.update(
                where={
                    "id": jobId,
                },
                data={"status": STATUS.PENDING, "completedItems": {"increment": 1}},
            )

            revalidate(trigger, STATUS.PENDING, TYPE.ARTICLE_GENERATION)

        else:
            await db.job.update(
                where={
                    "id": jobId,
                },
                data={
                    "status": STATUS.FAILED,
                    "error": "Missing article in response from AI Agents",
                },
            )

            revalidate(trigger, STATUS.FAILED, TYPE.ARTICLE_GENERATION)

            print("Skipping webhook due to empty article.")

        if usage_json and usage_json.get("total_tokens"):
            await db.usagemetric.create(
                data={
                    "trigger": trigger,
                    "date": usage_json.get("date"),
                    "promptTokens": usage_json.get("prompt_tokens"),
                    "completionTokens": usage_json.get("completion_tokens"),
                    "totalTokens": usage_json.get("total_tokens"),
                    "successfulRequests": usage_json.get("successful_requests"),
                    "jobId": jobId,
                }
            )

            revalidate(trigger, STATUS.COMPLETED, TYPE.ARTICLE_GENERATION)

        return {"ok": True, "message": "Article saved"}

    except Exception as e:
        print(f"run_article_writer_crew failed for {title}: {e}")
        await db.job.update(
            where={
                "id": jobId,
            },
            data={
                "status": STATUS.FAILED,
                "error": str(e),
            },
        )

        revalidate(trigger, STATUS.FAILED, TYPE.ARTICLE_GENERATION)

        return {"ok": False, "message": "No article generated"}

    finally:
        print("Closing Database Connection")


def run_article_writer_crew(*args, **kwargs):
    return asyncio.run(run_article_writer_crew_async(*args, **kwargs))
