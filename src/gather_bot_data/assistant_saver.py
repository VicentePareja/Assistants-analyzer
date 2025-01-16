from parameters import PATH_ASSISTANTS_DIRECTORY

class AssistantSaver:
    def __init__(self):
        self.assistants_directory = PATH_ASSISTANTS_DIRECTORY

    def save(self, assistant_name: str, assistant_id: str):
        with open(self.assistants_directory + f"/{assistant_name}.txt", "w", encoding="utf-8") as f:
            f.write(f"{assistant_name, assistant_id}\n")