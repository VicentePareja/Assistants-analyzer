# Assistants Analyzer

## Overview
Assistants Analyzer is a project designed to streamline the creation, testing, and evaluation of AI assistants. The project is structured to manage multiple AI assistants simultaneously, offering functionalities to:

1. **Gather Data:** Import and preprocess assistant data and test their responses.
2. **Analyze Data:** Generate reports and insights from the testing process.
3. **Evaluate Assistants:** Grade the AI's performance against human responses.

## Project Structure

### Root Directory
- **main.py**: Entry point of the project. Provides the option to gather data or skip directly to analysis.
- **parameters.py**: Defines the constants and configurations used across the project.
- **requirements.txt**: Lists all the Python dependencies required to run the project.
- **to_do.txt**: Placeholder for pending tasks.
- **.env**: Environment variables (e.g., API keys).

### Directories

#### **data/**
Contains all data related to the assistants and their evaluations.
- **assistants/**: Stores data for each assistant.
- **instructions/**: Contains assistant-specific instructions.
- **processed_results/**: Processed data ready for analysis.
- **reports/**: Generated analysis reports.
- **static_answers/**: Static test answers.
- **static_grades/**: Static test grades.
- **static_tests/**: Static test cases.

#### **src/**
Contains the source code for gathering, analyzing, and reporting data.

1. **analyze_bot_data/**
   - **create_report/**: Responsible for generating HTML reports.
     - `html_report_creator.py`: Generates reports summarizing analysis results.
     - `html_report_renderer.py`: Provides utilities to render HTML reports.
   - `paths_manager.py`: Manages file paths for data and results.
   - `analyze_bot_data.py`: Main script for data analysis.
   - `bot_data_loader.py`: Loads test data for analysis.
   - `bot_data_processor.py`: Processes and analyzes the loaded data.

2. **gather_bot_data/**
   - **create_assistant/**: Handles assistant creation and text processing.
     - `assistant_creator.py`: Automates the creation of AI assistants.
     - `doc_finder.py`: Locates Google Docs for assistant instructions.
     - `document_importer.py`: Imports text from Google Docs.
     - `text_separator_runner.py`: Separates text into instructions and examples.
   - **assistant_testing/**: Manages static tests for assistants.
     - `static_test_creator.py`: Creates static test cases.
     - `static_test_runner.py`: Runs static tests and stores results.
   - **assistant_grader/**: Grades assistant performance.
     - `assistant_grader.py`: Compares assistant answers with human responses.
   - `assistant_saver.py`: Saves assistant metadata.
   - `gather_bot_data.py`: Main script for gathering assistant data.

## Workflow

### 1. **Gathering Data**
The `GatherBotData` class orchestrates the data gathering process:
- **Create Assistant Instructions**: Extract instructions and examples from Google Docs.
- **Run Tests**: Generate test cases and execute them.
- **Grade Results**: Evaluate assistant performance.

### 2. **Analyzing Data**
The `BotDataAnalyzer` class processes the gathered data:
- **Load Data**: Loads test results for all assistants.
- **Analyze Performance**: Identifies best and worst responses, calculates differences, and extracts key insights.
- **Generate Reports**: Creates HTML reports summarizing findings.

### 3. **Configuration**
The `parameters.py` file defines:
- **Assistant Names**: List of all assistants.
- **Models and Parameters**: AI model and testing parameters.
- **Paths**: Directory paths for data, reports, and templates.
- **Evaluation Guidelines**: Criteria and scoring instructions for grading.

## Key Functionalities

### Assistant Creation
- Automates the separation of instructional text and examples.
- Supports multiple AI assistants with custom configurations.

### Testing and Grading
- Runs static tests on predefined questions.
- Evaluates responses with a detailed scoring system.

### Reporting
- Generates clean and insightful HTML reports.
- Highlights best, worst, and most diverse performance cases.

## Example Parameters (parameters.py)

### Assistant Settings
```python
BOTS_NAMES = [
    "MyU",
    "Ai Bot You",
    "Spencer Consulting",
    "Oncoprecisión",
    "Laboratorio Biomed",
    "Trayecto Bookstore",
    "Ortodoncia de la Fuente",
    "KLIK Muebles",
    "Nomad Genetics",
    "House of Spencer"
]
BASE_MODEL = "gpt-4o-mini-2024-07-18"
BASE_TEMPERATURE = 0.5
BASE_TOP_P = 1
```

### Text Separator
```python
SEPARATOR_MODEL = "o1-mini-2024-09-12"
DEVELOPER_TEXT_SEPARATOR_DESCRIPTION = """
You are a text processing AI. Your goal is to split the given text into two parts...
"""
```

### Paths
```python
PATH_INSTRUCTIONS_DIRECTORY = f"data/instructions"
PATH_ASSISTANTS_DIRECTORY = f"data/assistants"
PATH_STATIC_TESTS_DIRECTORY = f"data/static_tests"
PATH_STATIC_ANSWERS_DIRECTORY = f"data/static_answers"
PATH_STATIC_GRADES_DIRECTORY = f"data/static_grades"
PATH_PROCESSED_RESULTS_DIRECTORY = f"data/processed_results"
PATH_REPORTS_DIRECTORY = f"data/reports"
```

## Usage

### Running the Project
1. **Gather Data**:
   ```bash
   python main.py
   ```
   Select "yes" to gather data for all assistants.

2. **Analyze Data**:
   The analysis will run automatically after data gathering or can be executed separately by skipping the data gathering step.

### Reports
Generated reports are stored in the `data/reports` directory. They include:
- Overview of assistant performance.
- Highlights of best and worst responses.
- Detailed analysis of differences in performance.

## Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Future Improvements
- Add support for dynamic testing scenarios.
- Implement advanced grading metrics.
- Enhance reporting capabilities with interactive visualizations.

## Notes
- Ensure the `.env` file contains valid API keys for OpenAI and Google services.
- Follow the `parameters.py` structure for consistent configuration management.