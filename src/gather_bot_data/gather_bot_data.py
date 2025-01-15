import os

from src.gather_bot_data.create_assistant.doc_finder import AssistantDocFinder
from src.gather_bot_data.create_assistant.document_importer import DocumentImporter
from src.gather_bot_data.create_assistant.text_separator_runner import TextSeparatorRunner
from parameters import *

class GatherBotData:
    def __init__(self):
        pass

    def create_assistant(self):
        self.create_instructions()
        self.create_openai_assistant()

    def create_instructions(self):
        self.find_doc_id()
        self.import_text_from_google_doc()
        self.separate_text()

    def find_doc_id(self):
        finder = AssistantDocFinder()
        assistant_id, gdocs_address = finder.get_doc_id_by_assistant_name(self.assistant_name)
        self.document_id = gdocs_address

    def import_text_from_google_doc(self):
        importer = DocumentImporter(
            service_account_path=PATH_GOOGLE_SERVICE_ACCOUNT,
            document_id=self.document_id,
            instructions_dir_path=PATH_INSTRUCTIONS_DIRECTORY, 
            project_name=self.assistant_name
        )
        importer.import_text()

    def separate_text(self):
        separator_runner = TextSeparatorRunner(
            api_key= os.getenv("OPENAI_API_KEY"),
            assistant_id=os.getenv("ID_ASSISTANT_TEXT_SEPARATOR"), 
            assistant_name=self.assistant_name
        )
        separator_runner.run()

    def create_openai_assistant(self):
        pass

    def create_static_test(self):
        pass

    def get_assistant_answers(self):
        pass

    def create_evaluator(self):
        pass

    def grade_assistant(self):
        pass

    def unify_data(self):
        pass

    def get_data(self, assistant_name):
        self.assistant_name = assistant_name

        print(f"Getting data for assistant: {assistant_name}")
        
        self.create_assistant()
        self.create_static_test()
        self.get_assistant_answers()
        

        self.create_evaluator()
        self.grade_assistant()
        self.unify_data()