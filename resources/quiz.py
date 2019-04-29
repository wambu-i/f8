import json

quiz = "agoa.json"

def import_questions():
    questions = {}
    try:
        with open(quiz, "r") as store:
            questions = json.load(store)
            store.close()
    except (IOError, OSError):
        return None

    return questions

questions = import_questions()

def handle_quiz(idx):
	qu = questions.get(str(idx + 1), None)
	print(qu)

print(handle_quiz(0))