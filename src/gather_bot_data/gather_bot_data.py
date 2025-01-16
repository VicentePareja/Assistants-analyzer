import os
import time

from src.gather_bot_data.create_assistant.doc_finder import AssistantDocFinder
from src.gather_bot_data.create_assistant.document_importer import DocumentImporter
from src.gather_bot_data.create_assistant.text_separator_runner import TextSeparatorRunner
from src.gather_bot_data.create_assistant.assistant_creator import AssistantCreator
from src.gather_bot_data.assistant_saver import AssistantSaver
from src.gather_bot_data.assistant_testing.static_test_creator import StaticTestCreator
from src.gather_bot_data.assistant_testing.static_test_runner import StaticAssistantRunner
from src.gather_bot_data.assistant_grader.assistant_grader import AssistantGrader
from parameters import *

class GatherBotData:
    def __init__(self):
        self.assistant_saver = AssistantSaver()
        self.finder = AssistantDocFinder()
        self.importer = DocumentImporter(
            service_account_path=PATH_GOOGLE_SERVICE_ACCOUNT,
            instructions_dir_path=PATH_INSTRUCTIONS_DIRECTORY, 
        )
        self.text_separator_runner = TextSeparatorRunner(api_key= os.getenv("OPENAI_API_KEY"),
                                                          separator_assistant_id=os.getenv("ID_ASSISTANT_TEXT_SEPARATOR"))
        self.assistant_creator = AssistantCreator(api_key=os.getenv("OPENAI_API_KEY"))
        self.static_test_creator = StaticTestCreator()
        self.static_test_runner = StaticAssistantRunner(openai_api_key=os.getenv("OPENAI_API_KEY"),
                                                        assistant_ids_path=PATH_ASSISTANTS_DIRECTORY,
                                                        test_cases_path=PATH_STATIC_TESTS_DIRECTORY,
                                                        answers_path=PATH_STATIC_ANSWERS_DIRECTORY)
        self.assistant_grader = AssistantGrader(openai_api_key=os.getenv("OPENAI_API_KEY"), 
                                                instructions_dir_path=PATH_INSTRUCTIONS_DIRECTORY,
                                                answers_dir_path=PATH_STATIC_ANSWERS_DIRECTORY,
                                                grades_dir_path=PATH_STATIC_GRADES_DIRECTORY)


    def create_assistant(self):
        self.create_instructions()
        self.create_openai_assistant()

    def create_instructions(self):
        self.find_doc_id()
        self.import_text_from_google_doc()
        self.separate_text()

    def find_doc_id(self):
        assistant_id, gdocs_address = self.finder.get_doc_id_by_assistant_name(self.assistant_name)
        self.document_id = gdocs_address

    def import_text_from_google_doc(self):
        self.importer.import_text(self.assistant_name, self.document_id)

    def separate_text(self):
        self.text_separator_runner.run(self.assistant_name)

    def create_openai_assistant(self):
        
        assistant = self.assistant_creator.create_assistant(
            name=self.assistant_name,
            model=BASE_MODEL,
            tools=[],
            temperature=BASE_TEMPERATURE,
            top_p=BASE_TEMPERATURE
        )

        self.assistant_saver.save(
            assistant.name,
            assistant.id,
        )

    def create_static_test(self):
        self.static_test_creator.create_worst_of_4_test(self.assistant_name)
        self.static_test_creator.create_single_assessment_test(self.assistant_name)

    def get_assistant_answers(self):
        self.static_test_runner.run_all_worst_of_4_tests(self.assistant_name)
        self.static_test_runner.run_all_single_assessment_tests(self.assistant_name)

    def create_evaluator(self):
        pass

    def grade_assistant(self):
        pass

    def unify_data(self):
        pass

    def get_data(self, assistant_name):
        self.assistant_name = assistant_name
        starting_time = time.time()
        print(f"Getting data for assistant: {assistant_name} at {starting_time}")
        
        #self.create_assistant()
        #self.create_static_test()
        #self.get_assistant_answers()
        
        self.grade_assistant()
        #self.unify_data()

        print(f"finsh getting data from {assistant_name}. It took {(time.time()-starting_time):.2f} seconds.")