import json


def import_questions(path):
    questions = []
    try:
        with open(path, "r") as store:
            questions = json.load(store)
            store.close()
    except (IOError, OSError):
        return None

    return questions
