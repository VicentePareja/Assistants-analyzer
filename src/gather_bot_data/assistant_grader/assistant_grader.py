import csv
import os
import openai
from parameters import DEVELOPER_INTRO, DEVELOPER_DESCRIPTION

class AssistantGrader:
    def __init__(self, openai_api_key, instructions_dir_path, answers_dir_path, grades_dir_path):
        self.openai_api_key = openai_api_key
        self.instructions_dir_path = instructions_dir_path
        self.answers_dir_path = answers_dir_path
        self.grades_dir_path = grades_dir_path
        self.developer_intro = DEVELOPER_INTRO
        self.developer_description = DEVELOPER_DESCRIPTION
        
        openai.api_key = self.openai_api_key

    def grade_assistant(self, assistant_name):
        """
        Main entry point for grading an assistant. 
        """
        self.assistant_name = assistant_name
        self.update_paths()
        
        self.grade_worst_of_4_tests()
        self.grade_single_assessment_tests()

    def update_paths(self):
        """
        Updates all relevant file paths based on the assistant name.
        """
        self.without_examples_instructions_file_path = (
            f"{self.instructions_dir_path}/{self.assistant_name}_instructions_without_examples.txt"
        )
        self.worst_of_4_answers_file_path = (
            f"{self.answers_dir_path}/{self.assistant_name}_answers_worst_of_4.csv"
        )
        self.worst_of_4_grades_file_path = (
            f"{self.grades_dir_path}/{self.assistant_name}_grades_worst_of_4.csv"
        )
        self.single_assessment_answers_file_path = (
            f"{self.answers_dir_path}/{self.assistant_name}_answers_single_assessment.csv"
        )
        self.single_assessment_grades_file_path = (
            f"{self.grades_dir_path}/{self.assistant_name}_grades_single_assessment.csv"
        )

    def grade_worst_of_4_tests(self):
        """
        Reads the 'worst_of_4' answers CSV, prompts OpenAI to perform a grading
        for each row, and writes the results to the corresponding grades CSV.
        """
        with open(self.without_examples_instructions_file_path, mode="r", encoding="utf-8") as f:
            assistant_context = f.read()

        self._grade_test(
            input_csv_path=self.worst_of_4_answers_file_path,
            output_csv_path=self.worst_of_4_grades_file_path,
            developer_intro=self.developer_intro,
            assistant_context=assistant_context,
            evaluation_description=self.developer_description,
        )

    def grade_single_assessment_tests(self):
        """
        Reads the 'single_assessment' answers CSV, prompts OpenAI to perform a grading
        for each row, and writes the results to the corresponding grades CSV.
        """
        # Example developer/system instructions for grading

        with open(self.without_examples_instructions_file_path, mode="r", encoding="utf-8") as f:
            assistant_context = f.read()

        self._grade_test(
            input_csv_path=self.single_assessment_answers_file_path,
            output_csv_path=self.single_assessment_grades_file_path,
            developer_intro=self.developer_intro,
            assistant_context=assistant_context,
            evaluation_description=self.developer_description
        )

    def _grade_test(self, input_csv_path, output_csv_path,
                    developer_intro, assistant_context, evaluation_description):
        """
        General-purpose grader that reads a CSV of format:
        
            Question;Human Answer;[AssistantName]

        Crafts a prompt to evaluate each row, calls OpenAI, 
        and writes the grading to output_csv_path.
        """

        graded_rows = []
        with open(input_csv_path, mode="r", encoding="utf-8") as infile:
            reader = csv.reader(infile, delimiter=";")
            
            # If the CSV has headers, you could store them:
            # header = next(reader)  # skipping the header if present

            for row in reader:
                # Expected CSV structure:
                # row[0] -> Question
                # row[1] -> Human Answer
                # row[2] -> Assistant's Machine Answer

                question = row[0]
                human_answer = row[1]
                machine_answer = row[2] if len(row) > 2 else ""

                # Compose chat messages according to your grading format:
                messages = [
                    {
                        "role": "developer",
                        "content": (
                            f"The developer says:\n\n"
                            f"{developer_intro}\n\n"
                            f"{assistant_context}\n\n"
                            f"{evaluation_description}"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Pregunta:\n{question}\n\n"
                            f"Respuesta humana:\n{human_answer}\n\n"
                            f"Respuesta de la máquina:\n{machine_answer}"
                        ),
                    },
                ]

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o",  # or whichever model you want
                        messages=[
                            {
                                "role": "developer",
                                "content": messages[0]["content"]
                            },
                            {
                                "role": "user",
                                "content": messages[1]["content"]
                            }
                        ],
                        temperature=0.0,  # For consistent grading, keep temperature low
                    )
                    grade_response = response.choices[0].message["content"].strip()
                except Exception as e:
                    grade_response = f"Error: {str(e)}"

                # Append final results
                graded_rows.append([question, human_answer, machine_answer, grade_response])

        # Write out the graded CSV
        with open(output_csv_path, mode="w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile, delimiter=";")
            # Optionally include a header:
            writer.writerow(["Question", "Human Answer", "Machine Answer", "Grading"])
            writer.writerows(graded_rows)
