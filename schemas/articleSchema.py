def ArticleEntity(item) -> dict:
    """
    Converts a topic item to a dictionary representation.

    Args:
        item: The topic item to convert.

    Returns:
        A dictionary representation of the topic item.
    """

    if item is None:
        return {
            "title": None,
            "summary": None,
            "published": None,
            "sources": None,
            "categoryId": None,
            "jobId": None,
            "trigger": None,
            "topicId": None,
        }
    else:
        return {
            "title": item.title,
            "summary": item.summary,
            "published": item.published,
            "sources": item.sources,
            "categoryId": item.categoryId,
            "jobId": item.jobId,
            "trigger": item.trigger,
            "topicId": item.topicId,
        }
