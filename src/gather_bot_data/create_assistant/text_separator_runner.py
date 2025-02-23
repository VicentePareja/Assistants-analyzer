import sys
sys.stdout.reconfigure(encoding='utf-8')  # Ensure UTF-8 output

import json
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override
from parameters import PATH_INSTRUCTIONS_DIRECTORY, SEPARATOR_MODEL, DEVELOPER_TEXT_SEPARATOR_DESCRIPTION  # <-- Adjust if needed

################################################################################
# EventHandler: Handles streaming events from OpenAI (already OOP).
# (We won't use the streaming approach anymore, but we'll leave the class here.)
################################################################################
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        pass

    @override
    def on_text_delta(self, delta, snapshot):
        pass

    def on_tool_call_created(self, tool_call):
        pass

    def on_tool_call_delta(self, delta, snapshot):
        pass


################################################################################
# TextSeparator: Our main OOP class that handles reading instructions,
# calling OpenAI, extracting JSON, and saving results.
################################################################################
class TextSeparator:
    def __init__(self, api_key: str):
        """
        :param api_key: Your OpenAI API key
        :param assistant_id: The ID of your target assistant on OpenAI
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def run(self, assistant_name: str):
        """
        Reads the instructions file, sends it to the assistant, 
        extracts JSON, writes text outputs, etc.
        """
        print(f"Starting the TextSeparator run process for {assistant_name}.")

        self.path_intructions_no_examples = PATH_INSTRUCTIONS_DIRECTORY + f"/{assistant_name}_instructions_no_examples.txt"
        self.path_intructions_txt = PATH_INSTRUCTIONS_DIRECTORY + f"/{assistant_name}_original_instructions.txt"
        self.path_examples_txt = PATH_INSTRUCTIONS_DIRECTORY + f"/{assistant_name}_examples.txt"

        # 1. Read your instructions from a local file
        prompt = self._read_instructions(self.path_intructions_txt)

        # 2. Send prompt to the assistant and capture the combined response
        combined_response = self._ask_assistant(prompt)

        if not combined_response:
            print("No valid response from assistant or error encountered.")
            return
        
        # 3. Extract the JSON portion from the combined response
        actual_json_str = self._extract_json(combined_response)

        if not actual_json_str:
            print("No JSON object found in the response.")
            return

        # 4. Parse that JSON
        text_without_examples, only_examples = self._parse_json(actual_json_str)

        if text_without_examples is None and only_examples is None:
            print("Failed to parse JSON.")
            return

        # 5. Write the results to file
        self._write_results(text_without_examples, only_examples)
        print(
            f"Saved JSON fields into '{self.path_intructions_no_examples}' "
            f"and '{self.path_examples_txt}'"
        )

    ########################################################################
    # Internal helper methods
    ########################################################################
    def _read_instructions(self, file_path: str) -> str:
        """
        Reads the entire instructions file as a string.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def _ask_assistant(self, prompt: str) -> str:
        """
        Sends `prompt` to the assistant using a Chat Completion call
        and returns the assistant's response text as a single string.
        """
        try:
            # Prepare the messages in the same style as your working code
            messages = [
                {
                    "role": "developer",
                    "content": (f"{DEVELOPER_TEXT_SEPARATOR_DESCRIPTION}")                
                },
                {
                    "role": "user",
                    "content": (
                        f"{prompt}\n\n"
                    ),
                }
            ]

            # Call the chat completion endpoint
            response = self.client.chat.completions.create(
                model=SEPARATOR_MODEL,
                messages=messages,
                temperature=0.0
            )

            # Extract the text from the assistant
            return response.choices[0].message.content

        except Exception as e:
            print(f"Error running prompt: {e}")
            return ""

    def _extract_json(self, combined_response: str) -> str:
        """
        1) Find the first '{' and the last '}'.
        2) Extract that substring.
        3) Clean it up with _clean_extracted_json_str (intermediate step).
        """
        start_idx = combined_response.find("{")
        end_idx = combined_response.rfind("}")
        if start_idx == -1 or end_idx == -1:
            return ""

        extracted = combined_response[start_idx:end_idx + 1]
        cleaned = self._clean_extracted_json_str(extracted)
        return cleaned

    def _clean_extracted_json_str(self, text: str) -> str:
        # 1) Strip leading/trailing whitespace (including \n)
        text = text.strip()

        text = text.replace("\\", "")
        text = text.replace("{n", "{")
        text = text.replace("n}", "}")
        text = text.replace("  ", " ")
        text = text.replace(",n", ",")
        text = text.replace("{ ", "{")

        return text

    def _parse_json(self, json_str: str):
        """
        Attempts to parse the JSON string. 
        Returns (text_without_examples, only_examples).
        If it fails, returns (None, None).
        """
        try:
            parsed_json = json.loads(json_str)
            text_without_examples = parsed_json.get("text_without_examples", "")
            only_examples = parsed_json.get("only_examples", "")
            return text_without_examples, only_examples

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None, None

    def _write_results(self, text_without_examples: str, only_examples):
        """
        Writes the extracted strings to the specified output files.
        """
        with open(self.path_intructions_no_examples, "w", encoding="utf-8") as f1:
            f1.write(text_without_examples)

        with open(self.path_examples_txt, "w", encoding="utf-8") as f2:
            # If only_examples is a list, we can dump as JSON. Otherwise, just write it directly.
            if isinstance(only_examples, list):
                f2.write(json.dumps(only_examples, ensure_ascii=False, indent=2))
            else:
                f2.write(str(only_examples))


class TextSeparatorRunner:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def run(self, assistant_name: str):
        separator = TextSeparator(
            api_key=self.api_key,
        )
        separator.run(assistant_name)
