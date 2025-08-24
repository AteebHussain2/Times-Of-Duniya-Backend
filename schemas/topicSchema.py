def TopicEntity(item) -> dict:
    """
    Converts a topic item to a dictionary representation.

    Args:
        item: The topic item to convert.

    Returns:
        A dictionary representation of the topic item.
    """
    if item is None:
        return {
            "min_topics": None,
            "max_topics": None,
            "time_duration": None,
            "excluded_titles": None,
        }
    else:
        return {
            "min_topics": item.min_topics,
            "max_topics": item.max_topics,
            "time_duration": item.time_duration,
            "excluded_titles": item.excluded_titles,
        }
    
def RetryTopicEntity(item) -> dict:
    """
    Converts a topic item to a dictionary representation.

    Args:
        item: The topic item to convert.

    Returns:
        A dictionary representation of the topic item.
    """
    if item is None:
        return {
            "min_topics": None,
            "max_topics": None,
            "time_duration": None,
            "excluded_titles": None,
            "categoryName": None,
            "categoryId": None,
            "jobId": None,
        }
    else:
        return {
            "min_topics": item.min_topics,
            "max_topics": item.max_topics,
            "time_duration": item.time_duration,
            "excluded_titles": item.excluded_titles,
            "categoryName": item.categoryName,
            "categoryId": item.categoryId,
            "jobId": item.jobId,
        }
