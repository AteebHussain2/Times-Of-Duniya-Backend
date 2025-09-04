from crewai_tools import SerperDevTool
from crewai import Agent, LLM
from textwrap import dedent
import os

search_tool = SerperDevTool()


class TopicReasearcherAgents:
    def __init__(self):
        self.llm = LLM(
            api_key=os.getenv("GROQ_API_KEY"),
            model="groq/meta-llama/llama-guard-4-12b",
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
            max_rpm=30,
            max_iter=5,
            max_retries=3,
            max_tokens=10000,
        )
