from lib.clean_crewai_response import clean_crewai_topics, clean_usage_tokens
from config.topic.agents import TopicReasearcherAgents
from config.topic.tasks import TopicReasearcherTasks
from config.manager.agents import ManagerAgents
from crewai import Crew, Process
from typing import List
from prisma.enums import STATUS
from prisma import Prisma
import asyncio
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")


class ResearcherCrew:
    def __init__(
        self,
        category,
        excluded_titles: List[str] = [],
        min_topics: int = 1,
        max_topics: int = 2,
        time_duration: str = "24 hours",
    ):
        self.category = category
        self.excluded_titles = excluded_titles
        self.min_topics = min_topics
        self.max_topics = max_topics
        self.time_duration = time_duration

    def run(self):
        # Defining custom agents and tasks in agents.py and tasks.py
        agents = TopicReasearcherAgents()
        tasks = TopicReasearcherTasks()

        # Custom Agents for trending topics
        expert_researcher = agents.expert_researcher()
        manager_agent = ManagerAgents().manager_agent()

        # Custom Tasks for trending topics
        fetch_trending = tasks.fetch_trending_topics(
            expert_researcher,
            self.category,
            self.excluded_titles,
            self.min_topics,
            self.max_topics,
            self.time_duration,
        )

        # Fetch Trending Topics
        CrewInstance = Crew(
            agents=[expert_researcher],
            tasks=[fetch_trending],
            cache=True,
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

        res = CrewInstance.kickoff()

        return res


async def run_researcher_crew_async(
    min_topics: int,
    max_topics: int,
    time_duration: str,
    excluded_titles: List[str],
    category: str,
    categoryId: int,
    trigger: str,
    jobId: int,
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

    try:
        # Initialize the Crew with provided parameters
        crew = ResearcherCrew(
            category=category,
            excluded_titles=excluded_titles,
            min_topics=min_topics,
            max_topics=max_topics,
            time_duration=time_duration,
        )

        # Run the Crew to get topics
        res = crew.run()

        data = getattr(res, "json_dict", None) or str(res)
        topics = clean_crewai_topics(data)

        metrics = getattr(res, "token_usage", None)
        usage_json = clean_usage_tokens(metrics) if metrics else DEFAULT_USAGE

        if topics and "root" in topics and topics["root"]:
            topic_records = [
                {
                    "jobId": jobId,
                    "categoryId": categoryId,
                    "title": t.get("title"),
                    "summary": t.get("summary"),
                    "source": t.get("source"),
                    "published": t.get("published"),
                    "status": STATUS.COMPLETED,
                }
                for t in topics["root"]
            ]
            await db.topic.create_many(data=topic_records)

            await db.job.update(
                where={
                    "id": jobId,
                },
                data={
                    "status": STATUS.PENDING,
                    "totalItems": len(topics["root"]),
                },
            )

            print(
                f"Successfully created {len(topics['root'])} topics for category {category}"
            )

        else:
            await db.job.update(
                where={
                    "id": jobId,
                },
                data={
                    "status": STATUS.FAILED,
                    "error": "Missing topics in response from AI Agents",
                },
            )

            print("Skipping run_research_crew due to missing empty topics.")

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

        return {"ok": True, "message": f"{len(topics['root'])} topics saved"}

    except Exception as e:
        print(f"run_researcher_crew failed for category {category}: {e}")
        await db.job.update(
            where={
                "id": jobId,
            },
            data={
                "status": STATUS.FAILED,
                "error": str(e),
            },
        )

        return {"ok": False, "message": f"No topics generated!"}

    finally:
        print("Closing Database Connection")


def run_researcher_crew(*args, **kwargs):
    return asyncio.run(run_researcher_crew_async(*args, **kwargs))
