import json
import csv
from parameters import COLUMN_HUMAN_ANSWER, COLUMN_QUESTION, PATH_STATIC_TESTS_DIRECTORY, PATH_INSTRUCTIONS_DIRECTORY
import re

class StaticTestCreator:
    def __init__(self):
        self.examples_directory = PATH_INSTRUCTIONS_DIRECTORY
        self.static_test_directory = PATH_STATIC_TESTS_DIRECTORY

    def create_worst_of_4_test(self, assistant_name: str):
        # Read the file content
        input_file = self.examples_directory + f"/{assistant_name}_examples.txt"
        with open(input_file, "r", encoding="utf-8") as file:
            raw_content = file.read()

        # Normalize quotes (convert single quotes to double quotes)
        normalized_content = re.sub(r"(?<!\\)'", '"', raw_content)

        try:
            data = json.loads(normalized_content)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return

        # Write to the CSV file
        output_test_file = self.static_test_directory + f"/{assistant_name}_worst_of_4_test.csv"
        with open(output_test_file, "w", newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            # Write the headers
            writer.writerow([COLUMN_QUESTION, COLUMN_HUMAN_ANSWER])
            
            # Write each question-answer pair 4 times
            for entry in data:
                for _ in range(4):  # Repeat each pair 4 times
                    writer.writerow([entry["Q"], entry["A"]])

        

        print(f"Base Test file created: {output_test_file}")

    def create_single_assessment_test(self, assistant_name):
        # Read the file content
        input_file = self.examples_directory + f"/{assistant_name}_examples.txt"
        with open(input_file, "r", encoding="utf-8") as file:
            raw_content = file.read()

        # Normalize quotes (convert single quotes to double quotes)
        normalized_content = re.sub(r"(?<!\\)'", '"', raw_content)

        try:
            # Parse the normalized content as JSON
            data = json.loads(normalized_content)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return

        # Write to the CSV file
        output_test_file = self.static_test_directory + f"/{assistant_name}_single_assessment_test.csv"
        with open(output_test_file, "w", newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            # Write the headers
            writer.writerow([COLUMN_QUESTION, COLUMN_HUMAN_ANSWER])
            
            # Write each question-answer pair once
            for entry in data:
                writer.writerow([entry["Q"], entry["A"]])

        print(f"Single Assessment Test file created: {output_test_file}")