import sys
sys.stdout.reconfigure(encoding='utf-8')  # Ensure UTF-8 output

import os
import time
import re
import csv
from openai import OpenAI
from tqdm import tqdm
from parameters import COLUMN_HUMAN_ANSWER, COLUMN_QUESTION


class StaticAssistantRunner:
    """
    A class that implements the 7-step flow you described:
      1) load assistants
      2) load questions
      3) create a thread for each question
      4) send all the questions
      5) create a run for each thread/assistant pair and poll until completed
      6) whenever a run is in state "completed" store the answer
      7) finish when every run is completed and all answers are saved
    """

    def __init__(self, openai_api_key: str, assistant_ids_path: str, test_cases_path: str, answers_path: str):
        self.api_key = openai_api_key
        self.assistant_ids_path = assistant_ids_path
        self.test_cases_dir_path = test_cases_path
        self.answers_dir_path = answers_path

        self.assistants_dict = {}  # {assistant_name: assistant_id}

        # For step 3 & 4, store a thread_id for each question index
        # We'll reuse each thread with a single question:
        #   thread_map[q_idx] = thread_id
        self.thread_map = {}

        # For step 5, we also need to store run_id for each (assistant, q_idx).
        #   run_map[(assistant_name, q_idx)] = run_id
        self.run_map = {}

        # For step 6, we store the final answers once the run is complete
        #   answers_map[(assistant_name, q_idx)] = answer
        self.answers_map = {}

    def load_assistants(self):
        """
        Reads the .txt file with lines of the form:
            ('Assistant Name', 'assistant_id')
        Stores results in self.assistants_dict as {assistant_name: assistant_id}.
        """
        self.assistants_dict.clear()
        self.assistant_id_path = self.assistant_ids_path + f"/{self.assistant_name}.txt"

        if not os.path.exists(self.assistant_id_path):
            print(f"Error: The file {self.assistant_id_path} does not exist.")
            return

        pattern = re.compile(r"\('([^']+)',\s*'([^']+)'\)")
        with open(self.assistant_id_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                match = pattern.match(line)
                if match:
                    assistant_name = match.group(1)
                    assistant_id = match.group(2)
                    self.assistants_dict[assistant_name] = assistant_id

        print(f"Loaded {len(self.assistants_dict)} assistants from {self.assistant_id_path}:")
        for name, asst_id in self.assistants_dict.items():
            print(f"  {name} => {asst_id}")

    def load_qa_data(self, test_file: str):
        """
        Reads the CSV file containing question,human_answer
        and stores it in a list of dicts: [{'question':..., 'human_answer':...}, ...].
        """
        self.qa_data = []
        if not os.path.exists(test_file):
            print(f"Error: The file {test_file} does not exist.")
            return

        with open(test_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                question = row.get(COLUMN_QUESTION, "").strip()
                human_answer = row.get(COLUMN_HUMAN_ANSWER, "").strip()
                self.qa_data.append({
                    COLUMN_QUESTION: question,
                    COLUMN_HUMAN_ANSWER: human_answer
                })

        print(f"Loaded {len(self.qa_data)} Q&A rows from {test_file}.")

    def create_threads_and_send_questions(self):
        """
        Steps 3 & 4:
          - Create a Thread for each question
          - Send the question in a user message
        """
        self.thread_map.clear()
        client = OpenAI(api_key=self.api_key)

        print("\n=== Creating a thread for each question and posting the user message ===\n")
        with tqdm(total=len(self.qa_data), desc="Creating threads") as pbar:
            for idx, qa_item in enumerate(self.qa_data):
                question = qa_item[COLUMN_QUESTION]

                try:
                    # 1) Create a new thread
                    thread = client.beta.threads.create()

                    # 2) Send the user question to the thread
                    client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=question
                    )

                    # 3) Store thread_id
                    self.thread_map[idx] = thread.id

                except Exception as e:
                    print(f"Error creating/sending question '{question}': {e}")
                    self.thread_map[idx] = None

                pbar.update(1)

    def create_runs(self):
        """
        Step 5 (part 1):
        For each thread (hence each question), create a run with each assistant.
        We do NOT wait in this function; we only store the run_id.
        """
        client = OpenAI(api_key=self.api_key)
        self.run_map.clear()

        total_runs = len(self.assistants_dict) * len(self.qa_data)
        print(f"\n=== Creating {total_runs} runs (1 per assistant per question) ===\n")

        with tqdm(total=total_runs, desc="Creating runs") as pbar:
            for idx in range(len(self.qa_data)):
                thread_id = self.thread_map.get(idx)
                if thread_id is None:
                    # Could not create a thread for that question, skip
                    for asst_name in self.assistants_dict:
                        self.run_map[(asst_name, idx)] = None
                    pbar.update(len(self.assistants_dict))
                    continue

                # For each assistant
                for asst_name, asst_id in self.assistants_dict.items():
                    try:
                        # Create run
                        run = client.beta.threads.runs.create(
                            thread_id=thread_id,
                            assistant_id=asst_id
                        )
                        # Store run id
                        self.run_map[(asst_name, idx)] = run.id
                    except Exception as e:
                        print(f"Error creating run for (assistant={asst_name}, thread={thread_id}): {e}")
                        self.run_map[(asst_name, idx)] = None
                    pbar.update(1)

    def poll_runs_until_complete(self, poll_interval: float = 3.0):
        """
        Step 5 (part 2):
        Keep polling each run until it is "completed" (or failed/expired).
        As soon as a run is "completed", we retrieve the final assistant message
        (Step 6) and store it in `self.answers_map`.
        We exit once all runs are in a terminal state (completed, failed, cancelled, etc.).
        """
        client = OpenAI(api_key=self.api_key)

        # Flatten out a list of all (assistant_name, question_idx) keys
        all_keys = list(self.run_map.keys())

        # We'll keep track of how many are in a terminal state
        self.answers_map.clear()
        completed_count = 0
        total_runs = len(all_keys)

        print(f"\n=== Polling {total_runs} runs until they complete ===\n")

        # Create a progress bar
        with tqdm(total=total_runs, desc="Polling runs", unit="run") as pbar:
            while completed_count < total_runs:
                completed_count = 0
                for key in all_keys:
                    asst_name, q_idx = key
                    run_id = self.run_map[key]
                    # If we never successfully created the run, skip
                    if run_id is None:
                        # Mark as completed (error)
                        completed_count += 1
                        if (key not in self.answers_map):
                            self.answers_map[key] = "Error: Run not created"
                        continue

                    # If we already have an answer, it means it's done or failed
                    if key in self.answers_map:
                        completed_count += 1
                        continue

                    # Otherwise, poll the run object
                    try:
                        run_obj = client.beta.threads.runs.retrieve(thread_id=self.thread_map[q_idx], run_id=run_id)
                        status = run_obj.status

                        if status in (
                            "completed",
                            "failed",
                            "cancelled",
                            "expired"
                        ):
                            # Mark as done
                            completed_count += 1
                            pbar.update(1)  # Update the progress bar

                            if status == "completed":
                                # Step 6: get final assistant message
                                answer_text = self._get_final_assistant_message(run_obj, q_idx)
                                self.answers_map[key] = answer_text
                            else:
                                # For other terminal statuses, store status as "answer"
                                self.answers_map[key] = f"Run ended with status={status}"
                    except Exception as e:
                        # Mark as done with an error
                        completed_count += 1
                        self.answers_map[key] = f"Error polling run {run_id}: {e}"

                # If not done, sleep
                if completed_count < total_runs:
                    time.sleep(poll_interval)

            print("\nAll runs reached a terminal state.")


    def _get_final_assistant_message(self, run_obj, q_idx: int) -> str:
        """
        Retrieves the final assistant message from the thread after the run is completed.
        We look for the last message with role='assistant' in the thread.
        """
        client = OpenAI(api_key=self.api_key)
        thread_id = self.thread_map.get(q_idx)
        if thread_id is None:
            return "Error: missing thread_id"

        # Fetch the entire thread messages
        try:
            messages = client.beta.threads.messages.list(thread_id=thread_id)
        except Exception as e:
            return f"Error: {e}"

        # Filter assistant messages
        assistant_messages = [m for m in messages if m.role == "assistant"]
        if not assistant_messages:
            return "No assistant messages found."

        # Get the last assistant message
        final_message = assistant_messages[-1]

        # If content is a list of blocks, combine the text blocks
        if isinstance(final_message.content, list):
            text_fragments = []
            for block in final_message.content:
                if hasattr(block, "type") and block.type == "text":
                    # Extract the value from the block's text field
                    if hasattr(block, "text") and hasattr(block.text, "value"):
                        text_fragments.append(block.text.value)

            try:
                return "".join(text_fragments)
            except Exception as e:
                return f"Error joining text fragments: {e}"
        else:
            # If content is a single string, return directly
            if isinstance(final_message.content, str):
                return final_message.content
            else:
                return "Error: Unexpected content type"



    def write_results_to_csv(self, output_file: str):
        """
        Step 7: Write everything (question, human_answer, and each assistant's final answer)
        to a new output CSV file.
        """
        fieldnames = [COLUMN_QUESTION, COLUMN_HUMAN_ANSWER] + list(self.assistants_dict.keys())

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
                writer = csv.DictWriter(out_f, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()

                for idx, qa_item in enumerate(self.qa_data):
                    row = {
                        COLUMN_QUESTION: qa_item[COLUMN_QUESTION],
                        COLUMN_HUMAN_ANSWER: qa_item[COLUMN_HUMAN_ANSWER],
                    }
                    # For each assistant, pull the final answer from self.answers_map
                    for asst_name in self.assistants_dict.keys():
                        answer = self.answers_map.get((asst_name, idx), "No data")
                        row[asst_name] = answer
                    writer.writerow(row)

            print(f"\nAnswers saved to {output_file}\n")
        except Exception as e:
            print(f"Error creating output CSV {output_file}: {e}")

    def update_paths(self):
        self.assistant_id_path = self.assistant_ids_path + f"/{self.assistant_name}.txt"
        self.worst_of_4_test_file = self.test_cases_dir_path + f"/{self.assistant_name}_worst_of_4_test.csv"
        self.answers_worst_of_4_file_path = self.answers_dir_path + f"/{self.assistant_name}_answers_worst_of_4.csv"
        self.single_assessment_test_file = self.test_cases_dir_path + f"/{self.assistant_name}_single_assessment_test.csv"
        self.answers_single_assessment_file_path = self.answers_dir_path + f"/{self.assistant_name}_answers_single_assessment.csv"

    def run_all_worst_of_4_tests(self, assistant_name: str):
        """
        Master flow that does steps 1..7:
        1) Load assistants
        2) Load Q&A
        3) Create a thread for each question
        4) Post the question as a user message
        5) Create a run for each (assistant, thread)
        6) Poll until runs are completed, store final answers
        7) Write results to CSV
        """
        # Record start time
        start_time = time.time()
        self.assistant_name = assistant_name

        self.update_paths()

        # 1) load assistants
        self.load_assistants()
        # 2) load Q&A
        self.load_qa_data(self.worst_of_4_test_file)

        if not self.assistants_dict or not self.qa_data:
            print("No assistants or QA data found. Exiting.")
            return

        # 3 & 4) Create a thread for each question and send user messages
        self.create_threads_and_send_questions()

        # 5) Create runs for each (assistant, question)
        self.create_runs()

        # 5 & 6) Poll runs until completed, retrieve final answers
        self.poll_runs_until_complete()

        # 7) Write everything to CSV
        self.write_results_to_csv(self.answers_worst_of_4_file_path)

        # Record end time and calculate total duration
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\nAnswers gathered in: {total_time:.2f} seconds")

    def run_all_single_assessment_tests(self, assistant_name: str):
        """
        Master flow that does steps 1..7:
        1) Load assistants
        2) Load Q&A
        3) Create a thread for each question
        4) Post the question as a user message
        5) Create a run for each (assistant, thread)
        6) Poll until runs are completed, store final answers
        7) Write results to CSV
        """
        # Record start time
        start_time = time.time()
        self.assistant_name = assistant_name

        self.update_paths()

        # 1) load assistants
        self.load_assistants()
        # 2) load Q&A
        self.load_qa_data(self.single_assessment_test_file)

        if not self.assistants_dict or not self.qa_data:
            print("No assistants or QA data found. Exiting.")
            return

        # 3 & 4) Create a thread for each question and send user messages
        self.create_threads_and_send_questions()

        # 5) Create runs for each (assistant, question)
        self.create_runs()

        # 5 & 6) Poll runs until completed, retrieve final answers
        self.poll_runs_until_complete()

        # 7) Write everything to CSV
        self.write_results_to_csv(self.answers_single_assessment_file_path)

        # Record end time and calculate total duration
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\nAnswers gathered in: {total_time:.2f} seconds")
