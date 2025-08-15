from pydantic import PydanticDeprecatedSince20
from tasks import NewsGenerationTasks
from agents import ReportingAgents
from crewai import Crew, Process
from dotenv import load_dotenv
import warnings
import random
import time
import json
import re
import os


load_dotenv()
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)


class TripCrew:
    def __init__(self, category, excluded_titles):
        self.category = category
        self.excluded_titles = excluded_titles

    def run(self):
        # Define your custom agents and tasks in agents.py and tasks.py
        agents = ReportingAgents()
        tasks = NewsGenerationTasks()

        # Custom Agents
        expert_researcher = agents.expert_researcher()
        informant = agents.informant()
        news_mentalist = agents.news_mentalist()
        final_editor = agents.final_editor()
        manager_agent = agents.manager_agent()

        # Custom Tasks
        fetch_trending = tasks.fetch_trending_topics(
            expert_researcher, self.category, self.excluded_titles
        )

        # Fetch Trending Topics
        AnalystCrew = Crew(
            agents=[expert_researcher],
            tasks=[fetch_trending],
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager_agent,
            max_rpm=15,
            memory=True,
            embedder={
                "provider": "google",
                "config": {
                    "api_key": os.getenv("GOOGLE_API_KEY"),
                    "model": "text-embedding-004",
                },
            },
        )

        res = AnalystCrew.kickoff()
        data = res.json_dict  # Already a Python dict

        hot_topics = data["root"] if "root" in data else data
        for topic in hot_topics:
            title = topic["title"]

            # Defining tasks for each topic
            research_task = tasks.gather_research_data(informant, title)
            write_task = tasks.write_news_article(news_mentalist, title)
            review_task = tasks.editorial_review(final_editor, title)

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
                        "api_key": os.getenv("GOOGLE_API_KEY"),
                        "model": "text-embedding-004",
                    },
                },
            )
            output = NewsLetterCrew.kickoff(inputs=topic)
            data = output.json_dict

            # Pretty-print JSON string
            json_str = json.dumps(data, indent=2, ensure_ascii=False)

            # Clean filename for title
            fname = "".join(x for x in title if x.isalnum() or x in (" ", "_")).rstrip()
            fname = "_".join(fname.split())[:100]  # replace spaces, limit length
            path = f"{fname}.md"

            with open(path, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"✅ Saved: {path}")
            time.sleep(random.randint(60, 180))

        return "Successfully generated news articles based on trending topics."


# This is the main function that you will use to run your custom crew.
if __name__ == "__main__":
    print("## Welcome to News Writter Crew")
    print("-------------------------------")
    # category = input("What is your category?")
    category = "Pakistan"
    # Excluded titles can be customized based on your requirements
    excluded_titles = [
        "Gunmen in Balochistan Pakistan Abduct and Kill Nine Bus Passengers",
        "Pakistan's Prime Minister Announces New Economic Reforms",
        "Pakistan's Cricket Team Wins Historic Match",
    ]

    reporter_crew = TripCrew(category, excluded_titles)
    result = reporter_crew.run()
    print("\n\n########################")
    print("## Here is your News Letter")
    print("########################\n")
    print(result)
