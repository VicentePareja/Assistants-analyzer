

class AssistantGrader:
    def __init__(self, assistant, grader):
        self.assistant = assistant
        self.grader = grader

    def grade_assistant(self):
        return self.grader.grade(self.assistant)