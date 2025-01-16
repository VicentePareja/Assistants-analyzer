BOTS_NAMES = [
    "MyU",
    "Ai Bot You",
    #"Spencer Consulting",
    #"Oncoprecisión",
    #"Laboratorio Biomed",
    #"Trayecto Bookstore",
    #"Ortodoncia de la Fuente",
    #"KLIK Muebles",
    #"Nomad Genetics",
    #"House of Spencer"
]

# Bots' parameters
BASE_MODEL = "gpt-4o-mini-2024-07-18" 
BASE_MODEL_SUFFIX = "base"     
BASE_TEMPERATURE = 0.5
BASE_TOP_P = 1

# Test parameters
COLUMN_QUESTION = "Question"
COLUMN_HUMAN_ANSWER = "Human Answer"

# Paths
PATH_INSTRUCTIONS_DIRECTORY = f"data/instructions"
PATH_ASSISTANTS_DIRECTORY = f"data/assistants"
PATH_STATIC_TESTS_DIRECTORY = f"data/static_tests"
PATH_STATIC_ANSWERS_DIRECTORY = f"data/static_answers"


    # Google Service Account
PATH_GOOGLE_SERVICE_ACCOUNT = f"google_service/aibotyou-assitantscreator-881108c39324.json"