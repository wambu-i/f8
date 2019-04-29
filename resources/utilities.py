import json
import os
path = os.path.abspath("agoa.json")
def import_questions(files):
    questions = []
    try:
        with open(path, "r") as store:
            questions = json.load(store)
            store.close()
    except (IOError, OSError):
        return None

    return questions
