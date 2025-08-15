from lib.clean_crewai_response import clean_crewai_topics, clean_usage_tokens
from config.topic.agents import TopicReasearcherAgents
from config.topic.tasks import TopicReasearcherTasks
from config.manager.agents import ManagerAgents
from crewai import Crew, Process
from typing import List
import requests
import json
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


def run_researcher_crew(
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
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "successful_requests": 0,
    }

    try:
        # Initialize the Crew with provided parameters
        crew = ResearcherCrew(
            category,
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
        try:
            usage_json = clean_usage_tokens(metrics) if metrics else DEFAULT_USAGE
        except:
            usage_json = DEFAULT_USAGE

        # Send topics to Next.js webhook if valid
        if topics:
            try:
                webhook_url = f"{FRONTEND_BASE_URL}/api/webhooks/topics"
                payload = {
                    "categoryId": categoryId,
                    "topics": topics["root"],
                    "trigger": trigger,
                    "status": "COMPLETED",
                    "usage": usage_json,
                    "jobId": jobId,
                }

                headers = {"authorization": f"Bearer {SECRET_KEY}"}

                response = requests.post(
                    webhook_url,
                    json=payload,
                    headers=headers,
                    timeout=30,
                )

                response.raise_for_status()
                print(f"Webhook success: {response.status_code}")
            except Exception as e:
                print(f"Webhook failed with error: {e}")
                print("Payload was:", json.dumps(payload, indent=2))

        else:
            print("Skipping webhook due to missing FRONTEND_BASE_URL or empty topics.")

        return topics

    except Exception as e:
        try:
            webhook_url = f"{FRONTEND_BASE_URL}/api/webhooks/topics"
            payload = {
                "categoryId": categoryId,
                "topics": [],
                "trigger": trigger,
                "status": "FAILED",
                "error": str(e),
                "usage": DEFAULT_USAGE,
                "jobId": jobId,
            }

            headers = {"authorization": f"Bearer {SECRET_KEY}"}

            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()
            print(f"Webhook success: {response.status_code}")
        except Exception as e:
            print(f"Webhook failed with error: {e}")
            print("Payload was:", json.dumps(payload, indent=2))
        print(f"run_researcher_crew failed for category {category}: {e}")
        return {"root": []}
