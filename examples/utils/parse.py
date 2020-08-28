from .exceptions import AmbiguousAnswerException
import re


def extract_sex(text, mapping):
    """Extracts sex keywords from text.

    Args:
        text (str): Text from which the keywords will be extracted.
        mapping (dict): Mapping from keyword to sex.

    Returns:
        str: Single decision (one of `mapping` values).

    Raises:
        AmbiguousAnswerException: If `text` contains keywords mapping to two
            or more different distinct sexes.
        ValueError: If no keywords can be found in `text`.

    """
    sex_keywords = set(extract_keywords(text, mapping.keys()))
    if len(sex_keywords) == 1:
        return mapping[sex_keywords.pop().lower()]
    else:
        raise AmbiguousAnswerException()


def extract_keywords(text, keywords):
    """Extracts keywords from text.

    Args:
        text (str): Text from which the keywords will be extracted.
        keywords (list): Keywords to look for.

    Returns:
        list: All keywords found in text.

    """
    # Construct an alternative regex pattern for each keyword (speeds up the
    # search). Note that keywords must me escaped as they could potentialy
    # contain regex-specific symbols, e.g. ?, *.
    pattern = r"|".join(r"\b{}\b".format(re.escape(keyword))
                        for keyword in keywords)
    mentions_regex = re.compile(pattern, flags=re.I)
    return mentions_regex.findall(text.lower())


def extract_age(text):
    """Extracts age from text.

    Args:
        text (str): Text from which the keywords will be extracted.

    Returns:
        str: Found number (as a string).

    Raises:
        AmbiguousAnswerException: If `text` contains two or more numbers.
        ValueError: If no numbers can be found in `text`.

    """
    ages = set(re.findall(r"\b\d+\b", text))
    if len(ages) == 1:
        return ages.pop()
    else:
        raise AmbiguousAnswerException()


def extract_decision(text, mapping):
    """Extracts decision keywords from text.

    Args:
        text (str): Text from which the keywords will be extracted.
        mapping (dict): Mapping from keyword to decision.

    Returns:
        str: Single decision (one of `mapping` values).

    Raises:
        AmbiguousAnswerException: If `text` contains keywords mapping to two
            or more different distinct decision.
        ValueError: If no keywords can be found in `text`.

    """
    decision_keywords = set(extract_keywords(text, mapping.keys()))
    if len(decision_keywords) == 1:
        return mapping[decision_keywords.pop().lower()]
    elif len(decision_keywords) > 1:
        raise AmbiguousAnswerException("The decision seemed ambiguous.")
    else:
        raise ValueError("No decision found.")


def is_hi(message):
    """
    Brute force method to catch intent of user.
    :param message:
    :return: Boolean response
    """
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens
               for g in ['buen día', 'buen dia', 'hola', 'wena', "buena", "ola"])
