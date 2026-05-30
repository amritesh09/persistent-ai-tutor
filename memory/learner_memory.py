import json
import os

PROFILE_PATH = "memory/profiles/student.json"

DEFAULT_PROFILE = {
    "student_name": "demo_student",
    "preferred_language": "english",
    "concepts": {}
}


def load_profile():
    if not os.path.exists(PROFILE_PATH):
        save_profile(DEFAULT_PROFILE)
        return DEFAULT_PROFILE

    with open(PROFILE_PATH, "r") as f:
        return json.load(f)


def save_profile(profile):
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)


def update_concept(profile, concept, mastery_delta=0.1, mistake=None):
    concepts = profile["concepts"]

    if concept not in concepts:
        concepts[concept] = {
        "mastery": 0.3,
        "mistakes": [],
        "times_seen": 0,
        "next_review": None
    }

    concepts[concept]["mastery"] += mastery_delta
    concepts[concept]["mastery"] = min(
        max(concepts[concept]["mastery"], 0),
        1
    )

    concepts[concept]["times_seen"] += 1

    if mistake:
        concepts[concept]["mistakes"].append(mistake)

    save_profile(profile)