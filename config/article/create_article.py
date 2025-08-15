from lib.clean_crewai_response import clean_crewai_article, clean_usage_tokens
from config.article.agents import ArticleWriterAgents
from config.article.tasks import ArticleWriterTasks
from config.manager.agents import ManagerAgents
from crewai import Crew, Process
from typing import List
import requests
import json
import os


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")


class ArticleWriterCrew:
    def __init__(self, title: str, summary: str, sources: str):
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


def run_article_writer_crew(
    title: str,
    summary: str,
    sources: str,
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
        "total_tokens": 0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "successful_requests": 0,
    }

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
        article = clean_crewai_article(data)

        metrics = getattr(res, "token_usage", None)
        try:
            usage_json = clean_usage_tokens(metrics) if metrics else DEFAULT_USAGE
        except:
            usage_json = DEFAULT_USAGE

        # Send topics to Next.js webhook if valid
        if article:
            try:
                webhook_url = f"{FRONTEND_BASE_URL}/api/webhooks/article"
                payload = {
                    "categoryId": categoryId,
                    "jobId": jobId,
                    "data": article,
                    "status": "COMPLETED",
                    "trigger": trigger,
                    "topicId": topicId,
                    "usage": usage_json,
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
            print("Skipping webhook due to empty article.")

        return article

    except Exception as e:
        try:
            webhook_url = f"{FRONTEND_BASE_URL}/api/webhooks/article"
            payload = {
                "categoryId": categoryId,
                "jobId": jobId,
                "data": [],
                "status": "FAILED",
                "trigger": trigger,
                "topicId": topicId,
                "error": str(e),
                "usage": DEFAULT_USAGE,
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
        print(f"run_article_writer_crew failed for topic {title}: {e}")
        return {}


# res is returning a json:
