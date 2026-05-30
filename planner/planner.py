from datetime import datetime, timedelta


def choose_action(concept_data):

    mastery = concept_data.get("mastery", 0)

    mistakes = concept_data.get("mistakes", [])

    times_seen = concept_data.get("times_seen", 0)

    # weak understanding
    if mastery < 0.3:
        return "SIMPLIFY"

    # repeated confusion
    if len(mistakes) >= 2:
        return "REVISE"

    # medium understanding
    if mastery < 0.7:
        return "EXPLAIN"

    # strong understanding
    return "QUIZ"


def next_review_date(mastery):

    days = 1

    if mastery > 0.5:
        days = 3

    if mastery > 0.8:
        days = 7

    return (
        datetime.now() + timedelta(days=days)
    ).strftime("%Y-%m-%d")