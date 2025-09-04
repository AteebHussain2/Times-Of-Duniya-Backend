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


def RegenerateArticleEntity(item) -> dict:
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
            "articleId": None,
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
            "articleId": item.articleId,
        }


def ManualArticleEntity(item) -> dict:
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
            "topicId": None,
            "userId": None,
            "trigger": None,
            "prompt": None,
        }
    else:
        return {
            "title": item.title,
            "summary": item.summary,
            "published": item.published,
            "sources": item.sources,
            "categoryId": item.categoryId,
            "jobId": item.jobId,
            "topicId": item.topicId,
            "userId": item.userId,
            "trigger": item.trigger,
            "prompt": item.prompt,
        }


def RegenerateManualArticleEntity(item) -> dict:
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
            "topicId": None,
            "userId": None,
            "articleId": None,
            "trigger": None,
            "prompt": None,
        }
    else:
        return {
            "title": item.title,
            "summary": item.summary,
            "published": item.published,
            "sources": item.sources,
            "categoryId": item.categoryId,
            "jobId": item.jobId,
            "topicId": item.topicId,
            "userId": item.userId,
            "articleId": item.articleId,
            "trigger": item.trigger,
            "prompt": item.prompt,
        }
