import sys
sys.stdout.reconfigure(encoding='utf-8')  # Ensure UTF-8 output

import json
import re
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
        actual_json_str = combined_response

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
            response = self.client.beta.chat.completions.parse(
                model=SEPARATOR_MODEL,
                messages=messages,
                temperature=0.0,
                response_format = {
                                    "type": "json_schema",
                                    "json_schema": {
                                        "name": "text_separator",
                                        "strict": True,
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "text_without_examples": {
                                                    "type": "string"
                                                },
                                                "examples": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            'Q': {"type": 'string'},
                                                            'A': {"type": 'string'}
                                                        },
                                                        "required": ["Q", "A"],
                                                        "additionalProperties": False
                                                    }
                                                }
                                            },
                                            "required": ["text_without_examples", "examples"],
                                            "additionalProperties": False
                                        }
                                    },
                                })

            # Extract the text from the assistant
            return response.choices[0].message.content

        except Exception as e:
            print(f"Error running prompt: {e}")
            return ""

    def _clean_extracted_json_str(self, text: str) -> str:
        """
        Cleans the extracted JSON string by handling escape sequences and formatting issues.
        """
        try:
            # Replace problematic escape sequences and trim the text
            text = text.strip()
            text = text.replace("\\", "\\\\")  # Escape backslashes
            text = text.replace("\n", "\\n")  # Preserve newline characters as literals
            text = text.replace("\t", "\\t")  # Preserve tab characters as literals
            text = text.replace('"', '\\"')  # Escape double quotes

            # Remove unnecessary whitespaces outside JSON structures
            text = ' '.join(text.split())
            return text

        except Exception as e:
            print(f"Error in cleaning JSON string: {e}")
            return ""

    def _parse_json(self, json_str: str):
        """
        Parses the cleaned JSON string and extracts fields.
        Returns (text_without_examples, only_examples).
        If parsing fails, attempts fallback recovery.
        """
        

        try:
            # Attempt parsing the JSON string
            parsed_json = json.loads(json_str)
            # Extract values from the parsed JSON object
            text_without_examples = parsed_json["text_without_examples"]
            only_examples = parsed_json["examples"]

            # Validate types
            if not isinstance(text_without_examples, str):
                print("Invalid type for 'text_without_examples'. Expected a string.")
                text_without_examples = ""

            if not isinstance(only_examples, list):
                print("Invalid type for 'only_examples'. Expected a list.")
                only_examples = []

            return text_without_examples, only_examples

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print("Attempting fallback recovery...")

            # Fallback strategy: Use a safer JSON decoder or log for manual review
            try:
                cleaned_json_str = re.sub(r'(?<!\\)"', '\\"', json_str)  # Escape any unescaped quotes
                parsed_json = json.loads(cleaned_json_str)
                return parsed_json.get("text_without_examples", ""), parsed_json.get("only_examples", [])
            except Exception as fallback_e:
                print(f"Fallback parsing failed: {fallback_e}")
                return None, None

        except Exception as e:
            print(f"Unexpected error during JSON parsing: {e}")
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
