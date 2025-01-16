
from openai import OpenAI
from parameters import PATH_INSTRUCTIONS_DIRECTORY

class AssistantCreator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def load_instructions(self, instructions_path) -> str:
        with open(instructions_path, 'r', encoding='utf-8') as file:
            return file.read()

    def create_assistant(self, name: str, model: str, tools: list, temperature = float, top_p = float):
        instructions = self.load_instructions(PATH_INSTRUCTIONS_DIRECTORY + f"/{name}_original_instructions.txt")
        print(f"Creating assistant with name: {name}")
        return self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model,
            temperature=temperature,
            top_p=top_p
        )