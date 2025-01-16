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
PATH_STATIC_GRADES_DIRECTORY = f"data/static_grades"
PATH_PROCESSED_RESULTS_DIRECTORY = f"data/processed_results"
PATH_REPORTS_DIRECTORY = f"data/reports"
PATH_TEMPLATES_DIRECTORY = f"src/templates"
    # Google Service Account
PATH_GOOGLE_SERVICE_ACCOUNT = f"google_service/aibotyou-assitantscreator-881108c39324.json"

# Evaluation parameters

EVAL_MODEL = "gpt-4o-mini-2024-07-18"

DEVELOPER_INTRO = """Eres una evaluador minusioso, exigente y cuidadoso. Tu labor es evaluar un asistente de IA y compararlo con respuestas humanas.
Es decir, se te entregara una pregunta y dos respuestas, una realizada por el humano y otra por el asistente de IA y debes compararlas.

Para que tengas contexto acerca del asistente, te dejo sus intrucciones:"""

DEVELOPER_DESCRIPTION = """Para evaluar esto lo haras con un número del 1 al 5.

1: La respuesta está totalmente incorrecta
2. La respuesta está incorrecta pero tiene algo de verdad
3. La respuesta es parcialemente correcta pero falta información
4. La respuesta es correcta pero inferior a la humana
5. La respuesta es tan o más buena que la humana

Responde con dos valores. El primero será la calificación y el segundo una justificación explicando el porqué de la calificación.

Ejemplo:

Pregunta: ¿Hacen pedidos a domicilio?
Respuesta Humana: Sí, hacemos pedidos a domicilio. 
Los pedidos a Santiago tienen un cobro de despacho de $2.000 y los pedidos al resto del país $4.000.

Respuesta del asistente: Sí, hacemos pedidos a domicilio.

Calificación: 3
Justificación: La respuesta del asistente es correcta pero le falta información importante como los costos de despacho.

Nota adicional: Has especial énfasis en la correcititud de datos como los enlaces o los numeros.

A continuación, se te entregará la pregunta, la respuesta humana y la pregunta del asistente."""