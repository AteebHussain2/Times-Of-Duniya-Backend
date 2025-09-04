from crewai import Agent, LLM
from textwrap import dedent
import os


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")


class ManagerAgents:
    def __init__(self):
        self.llm = LLM(
            api_key=GOOGLE_API_KEY,
            model="gemini/gemini-2.5-flash-lite",
            temperature=0.5,
        )

    def manager_agent(self):
        return Agent(
            role="Manager Agent",
            goal="Oversee the crew's operations, ensuring tasks are completed efficiently and effectively.",
            backstory=dedent(
                """
            A seasoned project manager with expertise in coordinating complex tasks.
            Skilled in resource allocation, task prioritization, and team management.
            Ensures that all agents work harmoniously towards the common goal of producing high-quality news content.
        """
            ),
            verbose=True,
            llm=self.llm,
            max_rpm=15,
            max_tokens=250000,
        )
