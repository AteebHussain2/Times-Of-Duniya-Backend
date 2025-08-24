from typing import List, Literal
from pydantic import BaseModel
from textwrap import dedent
from crewai import Task


class Article(BaseModel):
    title: str
    summary: str
    content: str
    tags: List[str]
    source: List[str]


class VerifiedArticle(BaseModel):
    accuracy_score: int
    reason: str
    status: Literal["APPROVED", "REJECTED"]
    feedback: str
    article: Article


class ArticleWriterTasks:
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

    def gather_research_data(self, agent, topic_title: str, summary: str, source: List[str] | str):
        return Task(
            description=dedent(
                f"""
            **Task**: Gather Related Research and Sources
            **Description**: Perform a comprehensive internet investigation for the topic "{topic_title}". 
            Collect credible facts, expert quotes, stats, background context, and reliable source URLs. 
            Do not include speculative, outdated, or low-credibility content.

            **Parameters**:
            - Topic Title: {topic_title}
            - Summary: {summary}
            - Original Source: {source}
            - Must from reliable sources:
            {self.__reliable_sources()}

            **Note**: {self.__tip_section()}
            """
            ),
            agent=agent,
            expected_output=dedent(
                """
                A detailed research summary in markdown or JSON format with:
                - important facts
                - expert quotes
                - statistics
                - historical context
                - list of credible source URLs
                """
            ),
        )

    def write_news_article(self, agent, topic_title: str, summary: str, context):
        return Task(
            description=dedent(
                f"""
            **Task**: Write a Newsworthy Article
            **Description**: Create a highly engaging, informative, and factual news article for the topic "{topic_title}".
            Use a neutral tone, avoid opinions or fluff. The article must contain:
            - A compelling title, 40 to 95 characters
            - A 2-3 sentence summary
            - A 1000 - 3800 characters body section
            - relevant tags, each seperated by commas in a list
            - A list of source URLs used in research

            **Parameters**:
            - Topic Title: {topic_title}
            - Summary: {summary}
            
            **NOTE**: Do NOT write the names of sources in sources list, but ONLY the URLs of sources
            **NOTE**: Do NOT write a blog or opinion piece. {self.__tip_section()}
            **NOTE**: Make sure that both values and keys are in double quotes in the JSON output
            """
            ),
            context=context,
            agent=agent,
            expected_output=dedent(
                """
                {
                  "title": "...",
                  "summary": "...",
                  "content": "...", (must be in well structerd markdown format)
                  "tags": ["...", "..."],
                  "sources": ["https://www.....", "..."]
                }
                """
            ),
            output_json=Article,
        )

    def editorial_review(
        self, agent, topic_title: str, summary: str, source: List[str] | str, context
    ):
        return Task(
            description=dedent(
                f"""
            **Task**: Final Editorial Review
            **Description**: Evaluate the drafted article for "{topic_title}". 
            Ensure it meets journalistic standards — objectivity, accuracy, relevance, clarity, on-brand tone, and newsworthiness.
            Approve only if it is a publishable news article — not a blog post or opinion piece.
            Give it an accuracy score from 0 to 100, where 100 is perfect accuracy.
            Provide detailed feedback on any issues, and if rejected, explain why it does not meet standards
            
            **You must output the FULL article JSON plus review details.**
            Return JSON like:
            {{
              "accuracy_score": 0 to 100, e.g. 85,
              "reason": "short reason"
              "status": "approved" | "rejected",
              "feedback": "detailed explanation",
              "article": {{
                "title": "...",
                "summary": "...",
                "content": "...",
                "tags": ["...", "..."],
                "sources": ["https://www...", "..."]
              }}
            }}
    
            **Parameters**:
            - Topic Title: {topic_title}
            - Summary: {summary}
            - Original Source: {source}
            - Reliable sources:
            {self.__reliable_sources()}

            **NOTE**: Do NOT write the names of sources in sources list, but ONLY the URLs of sources
            **NOTE**: Make sure that both values and keys are in double quotes in the JSON output
            **NOTE**: {self.__tip_section()}
            """
            ),
            agent=agent,
            async_execution=True,
            context=context,
            expected_output=dedent(
                """
                {
                  "accuracy_score": 0 to 100, e.g. 85,
                  "reason": "short reason"
                  "status": "APPROVED" | "REJECTED",
                  "feedback": "detailed explanation",
                  "article": {
                    "title": "...",
                    "summary": "...",
                    "content": "...",
                    "tags": ["...", "..."],
                    "sources": ["...", "..."]
                  }
                }
                """
            ),
            output_json=VerifiedArticle,
        )
