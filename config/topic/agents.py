from crewai_tools import SerperDevTool
from textwrap import dedent
from crewai import Agent, LLM
import os

search_tool = SerperDevTool()


class TopicReasearcherAgents:
    def __init__(self):
        self.llm = LLM(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini/gemini-2.0-flash",
            temperature=0.5,
        )

    def expert_researcher(self):
        return Agent(
            role="Trending Topic Analyst",
            goal="Find recent, high-engagement, newsworthy topics in the given category that are not already published.",
            backstory=dedent(
                """
            A digital news analyst specializing in identifying what is trending across the globe.
            Skilled at filtering news content from Google News, Reddit, Twitter/X, and global publications.
            Known for precision in relevance and recency detection (within specified time).
        """
            ),
            allow_delegation=False,
            tools=[search_tool],
            verbose=True,
            llm=self.llm,
            max_rpm=10,
            max_iter=5,
        )
