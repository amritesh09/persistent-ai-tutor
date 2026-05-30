from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq
import os

from memory.learner_memory import (
    load_profile,
    update_concept
)

from planner.planner import (
    choose_action,
    next_review_date
)

# -----------------------------
# GROQ CLIENT
# -----------------------------

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

# -----------------------------
# EMBEDDINGS + VECTOR DB
# -----------------------------

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

db = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)

# -----------------------------
# LOAD LEARNER PROFILE
# -----------------------------

profile = load_profile()

# -----------------------------
# SIMPLE CONCEPT DETECTION
# -----------------------------

def detect_concept(question):
    question = question.lower()

    if "fraction" in question:
        return "fractions"

    if "decimal" in question:
        return "decimals"

    if "algebra" in question:
        return "algebra"

    if "ratio" in question:
        return "ratios"

    return "general"


# -----------------------------
# MISTAKE DETECTION
# -----------------------------

def detect_mistake(question):
    question = question.lower()

    mistake_phrases = [
        "don't understand",
        "did not understand",
        "confused",
        "not clear",
        "hard",
        "difficult"
    ]

    for phrase in mistake_phrases:
        if phrase in question:
            return question

    return None


# -----------------------------
# MEMORY
# -----------------------------

conversation_memory = []

# -----------------------------
# START
# -----------------------------

print("\n===================================")
print("Persistent AI Tutor Ready!")
print("Type 'exit' to quit")
print("===================================\n")

while True:

    # -----------------------------
    # USER INPUT
    # -----------------------------

    question = input("Student: ")

    if question.lower() == "exit":
        break

    # -----------------------------
    # DETECT CONCEPT
    # -----------------------------

    concept = detect_concept(question)

    concept_data = profile["concepts"].get(concept, {})
    action = choose_action(concept_data)

    mastery = concept_data.get("mastery", 0.0)

    previous_mistakes = concept_data.get("mistakes", [])

    # -----------------------------
    # RETRIEVE NCERT CONTEXT
    # -----------------------------

    docs = db.similarity_search(question, k=3)

    context = "\n".join([
        doc.page_content for doc in docs
    ])

    # -----------------------------
    # RECENT MEMORY
    # -----------------------------

    recent_memory = "\n".join(
        conversation_memory[-4:]
    )

    # -----------------------------
    # ADAPTIVE TUTORING STYLE
    # -----------------------------

    tutoring_style = ""

    if action == "SIMPLIFY":
      tutoring_style = """
    - Explain VERY slowly
    - Use simple real-world analogies
    - Avoid difficult words
    - Revise basics first
    """

    elif action == "REVISE":
        tutoring_style = """
    - Revise previous mistakes
    - Focus on misconceptions
    - Ask short understanding checks
    """

    elif action == "QUIZ":
        tutoring_style = """
    - Ask conceptual quiz question
    - Encourage student to think
    - Do NOT immediately reveal answer
    """

    else:
        tutoring_style = """
    - Give medium difficulty explanation
    - Use one example
    - Ask conceptual follow-up question
    """

    # -----------------------------
    # PROMPT
    # -----------------------------

    prompt = f"""
You are a friendly AI tutor for Indian school students.

Student Profile:
- Current concept: {concept}
- Mastery level: {mastery}
- Previous mistakes: {previous_mistakes}
- Current tutoring action: {action}

Tutoring Instructions:
{tutoring_style}

General Rules:
- Explain clearly
- Use examples
- Be encouraging
- Use NCERT context
- Reply in same language as student
- Ask ONE follow-up question

Recent Conversation:
{recent_memory}

NCERT Context:
{context}

Student Question:
{question}
"""

    # -----------------------------
    # LLM CALL
    # -----------------------------

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = completion.choices[0].message.content

    # -----------------------------
    # DISPLAY ANSWER
    # -----------------------------

    print("\nTutor:")
    print(answer)

    # -----------------------------
    # UPDATE CONVERSATION MEMORY
    # -----------------------------

    conversation_memory.append(
        f"Student: {question}"
    )

    conversation_memory.append(
        f"Tutor: {answer}"
    )

    # -----------------------------
    # DETECT MISTAKES
    # -----------------------------

    mistake = detect_mistake(question)

    # -----------------------------
    # UPDATE LEARNER PROFILE
    # -----------------------------

    mastery_delta = 0.1

    if mistake:
        mastery_delta = -0.05

    update_concept(
        profile,
        concept,
        mastery_delta=mastery_delta,
        mistake=mistake
    )

    # reload updated profile
    profile = load_profile()

    updated_concept = profile["concepts"].get(concept)

    updated_concept["next_review"] = next_review_date(
        updated_concept["mastery"]
    )

    from memory.learner_memory import save_profile

    save_profile(profile)

    # -----------------------------
    # SHOW DEBUG INFO
    # -----------------------------

    updated_concept = profile["concepts"].get(concept, {})

    print("\n[DEBUG]")
    print(f"Concept: {concept}")
    print(f"Mastery: {updated_concept.get('mastery')}")
    print(f"Times Seen: {updated_concept.get('times_seen')}")
    print(f"Action: {action}")
    print(f"Next Review: {updated_concept.get('next_review')}")