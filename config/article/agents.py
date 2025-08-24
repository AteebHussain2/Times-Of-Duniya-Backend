from crewai_tools import SerperDevTool
from textwrap import dedent
from crewai import Agent
from crewai import LLM
import os

search_tool = SerperDevTool()


class ArticleWriterAgents:
    def __init__(self):
        self.llm = LLM(
            api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini/gemini-2.5-flash-lite",
            temperature=0.5,
        )

    def informant(self):
        return Agent(
            role="Internet Intelligence Gatherer",
            goal="Collect detailed, factual, and up-to-date information from multiple sources on a given news topic.",
            backstory=dedent(
                """
            A trained internet OSINT (Open Source Intelligence) specialist.
            Experienced in finding credible facts, expert opinions, stats, and links from the surface web and media archives.
            Known for delivering concise, trustworthy info without noise.
        """
            ),
            allow_delegation=False,
            tools=[search_tool],
            verbose=True,
            llm=self.llm,
            max_rpm=10,
            max_iter=5,
        )

    def news_mentalist(self):
        return Agent(
            role="News Article Writer",
            goal="Write engaging and factual news articles from a topic and research data without turning it into a blog or opinion piece.",
            backstory=dedent(
                """
            A professional content strategist and news writer trained in writing for digital audiences.
            Combines storytelling with journalistic tone — balancing engagement, clarity, and objectivity.
            Experienced in writing for politics, entertainment, tech, and crisis news.
        """
            ),
            allow_delegation=True,
            verbose=True,
            llm=self.llm,
            max_rpm=10,
            max_iter=3,
        )

    def final_editor(self):
        return Agent(
            role="Senior News Editor",
            goal="Review the article and ensure it meets journalistic standards. Approve only if it is news — not a blog, opinion, or fluff.",
            backstory=dedent(
                """
            A senior editorial professional responsible for maintaining the publication’s integrity.
            Reviews all submissions for clarity, objectivity, tone, factual accuracy, and public interest.
            Rejects content that lacks news value, reads like a blog, or violates platform guidelines.
        """
            ),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            max_rpm=10,
            max_iter=2,
        )
