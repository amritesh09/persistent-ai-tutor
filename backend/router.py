def choose_model(question, mastery):

    question = question.lower()

    simple_patterns = [
        "what is",
        "define",
        "meaning",
        "explain"
    ]

    if mastery < 0.3:
        return "large"

    for p in simple_patterns:
        if p in question:
            return "small"

    return "large"