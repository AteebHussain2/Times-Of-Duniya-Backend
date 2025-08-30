from pydantic import BaseModel
from datetime import datetime
from textwrap import dedent
from crewai import Task
from typing import List


class TrendingTopic(BaseModel):
    title: str
    summary: str
    source: List[str]
    published: str


class TrendingTopicList(BaseModel):
    root: List[TrendingTopic]


class TopicReasearcherTasks:
    def __tip_section(self):
        return (
            "If you do your BEST WORK, your news article will make headlines globally!"
        )

    def __reliable_sources(self):
        return [
            "https://www.reuters.com",
            "https://apnews.com",
            "https://www.bbc.com",
            "https://www.theguardian.com",
            "https://www.nytimes.com",
            "https://www.aljazeera.com/english/",
            "https://edition.cnn.com",
            "https://www.ft.com",
            "https://www.dw.com",
            "https://www.france24.com/en/",
            "https://www.abc.net.au/news/",
            "https://www.cbc.ca/news",
            "https://www3.nhk.or.jp/nhkworld/",
            "https://www.ndtv.com",
            "https://www.lemonde.fr/en/",
            "https://english.elpais.com/",
            "https://www.bloomberg.com",
            "https://www.wsj.com",
            "https://www.washingtonpost.com",
            "https://www.euronews.com",
            "https://www.afp.com/en",
            "https://www.latimes.com",
            "https://www.smh.com.au",
            "https://www.theglobeandmail.com",
            "https://www.independent.co.uk",
            "https://www.thetimes.co.uk",
            "https://www.bild.de",
            "https://www.faz.net/english/",
            "https://www.spiegel.de/international/",
            "https://zeenews.india.com",
            "https://www.aninews.in",
            "https://english.kyodonews.net",
            "https://www.yenisafak.com/en",
            "https://www.dailysabah.com/politics",
            "https://www.chinadaily.com.cn",
            "https://www.scmp.com",
            "https://www.gulfnews.com",
            "https://www.jordantimes.com",
            "https://www.timesofisrael.com",
            "https://www.ynetnews.com/en-US",
            "https://www.jpost.com",
            "https://www.iol.co.za/news/",
            "https://www.nation.africa",
            "https://www.premiumtimesng.com",
            "https://www.dailypost.ng",
            "https://punchng.com",
        ]

    def fetch_trending_topics(
        self,
        agent,
        category: str,
        exclude_titles: List[str],
        min_topics: int,
        max_topics: int,
        time_duration: str,
        prompt: str = "",
    ):
        exclusion = (
            "\n".join(f"- {title}" for title in exclude_titles)
            if exclude_titles
            else "None"
        )
        return Task(
            description=dedent(
                f"""
            **Task**: Identify Trending News Topics
            **Description**: Discover {min_topics} to {max_topics} highly relevant and trending news topics in the category **{category}**. 
            Only select topics that are less than {time_duration} old, Today is {datetime.now()}, have strong online engagement, and are not already covered by our platform. Use online sources like Google News, Twitter/X, Reddit, and top global news platforms.

            **ADDITIONAL INFORMATION**: {prompt if prompt else "None"}

            Return a JSON array like:
            [
              {{
                "title": "...",
                "summary": "...",
                "source": ["https://..."],
                "published": "YYYY-MM-DD"
              }},
              ...
            ]

            **Constraints**:
            - Minimum: {min_topics} Topics
            - Maximum: {max_topics} Topics
            - Published within last {time_duration}
            - Not in excluded titles:
            {exclusion}
            - Recommended if from reliable sources:
            {self.__reliable_sources()}
            - Can also be from Official Pakistan Government sources, if relevant.

            **Note**: {self.__tip_section()}
            """
            ),
            agent=agent,
            expected_output=dedent(
                """
                [
                  {
                    "title": "...",
                    "summary": "...",
                    "source": ["..."],
                    "published": "YYYY-MM-DD"
                  },
                  ...
                ]
                """
            ),
            output_json=TrendingTopicList,
        )
