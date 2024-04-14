# -*- coding: utf-8 -*-
import json


class user():
    def __init__(self, id, name=''):
        self.name = name
        self.is_premium = False
        self.level = 0
        self.id = id
        self.phone = None

    def upgrade_to_premium(self):
        self.is_premium = True


class test():
    class Question():
        def __init__(self, question_text, correct_answer, mod='chouse_answers', answers=None, link_to_picture=None):
            self.text = question_text
            self.mod = mod
            self.answers = answers
            self.difficulty_level = 1
            self.correct_answer = correct_answer

    def __init__(self, test_id: int, test_category_index: int):
        with open("tests.json", "r") as f:
            self.test_json = json.load(f)
            self.test_json = self.test_json[test_category_index]['tests_object_S'][test_id]
        self.name = self.test_json["name"]
        self.questions = [test.Question(question_text=a["question"], answers=a["answers"], correct_answer=a["correct"])
                          for a in self.test_json["questions"]]
        self.is_privat = self.test_json["need_phone_numder"]
        self.user_score = 0
        self.avtor = self.test_json["avtor"]
        self.question_id = 0
        self.message_if_win = self.test_json["if_win"]
        self.message_if_lose = self.test_json["if_lose"]
        if "first_message" not in self.test_json:
            self.test_json["first_message"] = "Желаю удачного прохождения"
        self.first_message = self.test_json["first_message"]


def user_message2test(text, id_user):
    questions = []
    stac = ''
    category = text[:text.index("}")]
    text = text[text.index("}") + 1:]
    s = text.index("}")
    test_in_process = {"name": text[:s], "typ": "", "need_phone_numder": False, "avtor": id_user,
                       "first_message": "Информация о вашем прохождении теста будет доступна автору теста и администрароторам проекта",
                       "if_win": "вы сдали данный тест", "if_lose": "Вы провалили тест, пройдите его ещё раз"}
    question = {"question": "", "answers": []}
    text = text[s + 1:]
    s = text.index("}")
    if s != 0:
        test_in_process["first_message"] = text[:s]
    text = text[s + 1:]

    i = 0

    while i < len(text):
        if text[i] == "?":
            question["question"] = stac + text[i]
            stac = ""
        elif text[i] == ")" and text[i - 1].isdigit():
            for t in range(i, len(text)):
                if text[t] == "\n":
                    question["answers"].append(text[int(i + 1):int(t)])
                    i = t
                    break
        elif text[i] == "]":
            stac = ''
            question["correct"] = int(text[i - 1]) - 1
            questions.append(question)
            question = {"question": "", "answers": []}

        elif text[i - 1] + text[i] == ']}':

            info = text[i:]
            info = info.split('/\\')
            test_in_process["if_win"] = info[0][1:]
            test_in_process["if_lose"] = info[1][:-2]
            break
        else:
            stac += text[i]
        i += 1
    for i in range(len(questions)):

        if any([len(b) > 25 for a in [questions[i]["answers"]] for b in a]):
            questions[i]["question"] = questions[i]["question"] + "\n\n выберите номер верного ответа"
            for j in range(len(questions[i]["answers"])):
                questions[i]["question"] = questions[i]["question"] + "\n\t" + str(j + 1) + ")\t" + \
                                           questions[i]["answers"][j]
            questions[i]["answers"] = list(set(range(1, 1 + len(questions[i]["answers"]))))
            questions[i]["correct"] = questions[i]["answers"].index(questions[i]["correct"] + 1)

    test_in_process["questions"] = questions

    with open("tests.json", "r") as f:
        t = json.load(f)
    if category in [a["name_category"] for a in t]:
        i = [a["name_category"] for a in t].index(category)
        t[i]["tests_object_S"].append(test_in_process)
    else:
        t.append({"name_category": category, "tests_object_S": [test_in_process]})

    with open("tests.json", "w") as f:
        f.write(json.dumps(t, indent=4))
    return True


def get_names_category():
    with open("tests.json", "r") as f:
        return [a["name_category"] for a in json.load(f)]


def category_index2names_test(category_index: int):
    with open("tests.json", "r") as f:
        return [a["name"] for a in json.load(f)[category_index]["tests_object_S"]]
