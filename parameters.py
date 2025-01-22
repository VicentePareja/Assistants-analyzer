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

# Text separator parameters
SEPARATOR_MODEL = "gpt-4o"
DEVELOPER_TEXT_SEPARATOR_DESCRIPTION = """
Eres una IA de procesamiento de texto. Tu objetivo es dividir el texto dado en dos partes y devolverlas estrictamente como JSON válido, sin texto adicional fuera del JSON. Las dos partes son:
1. "text_without_examples": Esto debe contener todo el texto de la entrada antes de que aparezca cualquier par de preguntas/respuestas de ejemplo.
2. "only_examples": Esto debe contener solo los pares de ejemplo en formato de lista JSON, algo como:
   [
     {'Q': '...','A': '...'},
     {'Q': '...', 'A': '...'}
   ]

   Observar que no puese haber comillas en los textos, solo en el JSON. Además, no es necesario escribir cosas como "asistente" o "usuario", se asume que la Q es del usuario y la A es del asistente.

### Pasos
1. Identifica dónde comienzan los pares de preguntas/respuestas de ejemplo (generalmente indicado por líneas que empiezan con "Q:" o una sección claramente marcada como "Ejemplo").
2. Extrae todo el texto antes de esta sección y colócalo bajo la clave "text_without_examples".
3. Extrae solo los pares de preguntas/respuestas, asegurándote de que las cadenas 'Q' y 'A' sean correctas. es importante que sea con 'Q' como key y 'A' como value. colócalos en la lista "only_examples".
4. No incluyas ningún texto adicional en "only_examples"; solo los pares de preguntas/respuestas.
5. Si no hay ejemplos, devuelve "only_examples" como un arreglo vacío.

### Required JSON Output Format
```json
{
  "text_without_examples": "All the text before any examples appear",
  "only_examples": "[{'Q':'question1', 'A':'answer1'}, {'Q':'question2', 'A':'answer2'}]" 
}

Siempre mantén ese formato.

Si hay diferentes ejemplos, agrégalos a la lista "only_examples".

Ejemplo:

Este es un asistente diseñado para satisfacer las necesidades del usuario.

Ejemplo 18: Q: ¿Entregan un reporte por cada sesión para poder reembolsar a la Isapre?
A: ¡Hola! 😊 No entregamos un reporte por sesión, pero nuestra boleta de servicios puede te permite reembolsar. Cuentanos si necesitas detallar el tipo de sesiones realizadas para facilitar tu reembolso con la Isapre. Contactanos directamente a https://walink.co/83468b para poder ayudarte mejor 📝 ¿Te ayudo con algo más?

Ejemplos de Conversaciones en Inglés:
Ejemplo 1:
Q: Hi, do you offer trial classes to get to know your services?
A: Hi there! 😊 Absolutely! You can book your free trial class here: 📲 https://boxmagic.cl/sp/HouseofSpencer24. Let me know if you need any help!

{
"text_without_examples": 'Este es un asistente diseñado para satisfacer las necesidades del usuario.',
"only_examples": "[{'Q:': '¿Entregan un reporte por cada sesión para poder reembolsar a la Isapre?', 'A': '¡Hola! 😊 No entregamos un reporte por sesión, pero nuestra boleta de servicios puede te permite reembolsar. Cuentanos si necesitas detallar el tipo de sesiones realizadas para facilitar tu reembolso con la Isapre. Contactanos directamente a https://walink.co/83468b para poder ayudarte mejor 📝 ¿Te ayudo con algo más?'}, 
{'Q': 'Hi, do you offer trial classes to get to know your services?', 'A': 'Hi there! 😊 Absolutely! You can book your free trial class here: 📲 https://boxmagic.cl/sp/HouseofSpencer24. Let me know if you need any help!
'}]"
}

### Casos borde a considerar:

1) Otra cosa que podría suceder es que haya muchas preguntas y respuestas en la misma conversación.

Ejemplo:

Usuario: "Hola, necesito el libro 'Fuego Celeste' de Alice Wolf. ¿Hacen despacho a Las Condes?"
Asistente (Trayectín): "¡Hola! Sí, despachamos a Las Condes. Puedes realizar tu pedido en nuestro sitio web. ¿Quisieras que te envíe el link?"
Usuario: "Sí."
Asistente (Trayectín): "Perfecto, visita nuestro sitio web en trayecto.cl. Ahí podrás completar tu pedido. ¿Necesitas algo más?"
Usuario: "No, muchas gracias."
Asistente (Trayectín): "Perfecto. Muchas gracias por preferir Trayecto Bookstore.

En este caso particular, debes extraer la pregunta principal y la respuesta principal:

{
"text_without_examples": "",
"only_examples": "[{'Q:': 'Hola, hacen despacho a las condes?', 'A': '¡Hola! Sí, despachamos a Las Condes. Puedes realizar tu pedido en nuestro sitio web. ¿Quisieras que te envíe el link?'}]"
}

Es muy importante que solo extraigas la pregunta principal y la respuesta principal. No incluyas las preguntas de seguimiento ni las respuestas de seguimiento.
cosas como "Sí" no son una pregunta válida, por lo que no se incluirá en el JSON.


2) Solo usa comillas simples y dobles para delimitar el JSON. Si algún texto tiene comillas simples o dobles, elimínalas. Repito, usa únicamente comillas simples y dobles para delimitar el JSON. NUNCA las uses en otros contextos; simplemente elimínalas.

Ejemplo:

"A": "¡Claro que sí! 😃 Para ayudarte, necesito que me indiques los siguientes datos: Nombre completo 📝 Dirección 🏠 Comuna 📍 Correo electrónico 📧 Marca de los equipos ❄️ (Ejemplo: Samsung, Midea, Otro) Número de equipos 🔢 ¿Quién instaló los equipos? ⚙️ (Opciones: "M&U" o "Tercero") Tipo de equipo 🔧 (Opciones: "Split" o "Multi-Split")"

Debería ser:

'A': '¡Claro que sí! 😃 Para ayudarte, necesito que me indiques los siguientes datos: Nombre completo 📝 Dirección 🏠 Comuna 📍 Correo electrónico 📧 Marca de los equipos ❄️ (Ejemplo: Samsung, Midea, Otro) Número de equipos 🔢 ¿Quién instaló los equipos? ⚙️ (Opciones: M&U o Tercero) Tipo de equipo 🔧 (Opciones: Split o Multi-Split)'

Otro ejemplo:

"Q": "Hola, necesito el libro 'Fuego Celeste' de Alice Wolf. ¿Hacen despacho a Las Condes?"

Debería ser:

"Q": "Hola, necesito el libro Fuego Celeste de Alice Wolf. ¿Hacen despacho a Las Condes?"

3) Si el texto está en inglés y hay una abreviatura como it's, don't, we're, etc., reemplázala con la forma completa.
It is, Do not, We are, etc.

Ejemplo:

Implementation of the Virtual Assistant
Customer: "Hi, I'm interested in implementing a virtual assistant for my business, but I'm worried it might be complicated."
Arturito: "Hi! 🤖 No need to worry; implementation is very straightforward. Our team takes care of the entire technical process. We just need to understand your needs, and within days, your assistant will be up and running effortlessly. We're here to make your life easier!" 🚀
{
"text_without_examples": "",
"only_examples": [{'Q': 'Hi, I am interested in implementing a virtual assistant for my business, but I am worried it might be complicated.','A': 'Hi! 🤖 No need to worry; implementation is very straightforward. Our team takes care of the entire technical process. We just need to understand your needs, and within days, your assistant will be up and running effortlessly. We are here to make your life easier!'}]
}

"""
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
PATH_TEMPLATES_DIRECTORY = f"src/analyze_bot_data/crate_report/templates"
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

# Analysis parameters
THRESHOLD = 4.5
BEST_WORST = 4
MOST_DIFFERENT = 3
# Report Styling Parameters
# parameters.py

# ------------------------------------------------------------------------------------
# Report Styling Parameters
# ------------------------------------------------------------------------------------
# parameters.py

# ------------------------------------------------------------------------------------
# Report Styling Parameters
# ------------------------------------------------------------------------------------
# Font and Text
REPORT_FONT_FAMILY = "Georgia, 'Times New Roman', serif"
REPORT_FONT_SIZE = "18px"
REPORT_TEXT_COLOR = "#444"  # Softer black for readability

# Headings
REPORT_HEADING_FONT_SIZE = "2em"  # Larger, more formal headings
REPORT_SUBHEADING_FONT_SIZE = "1.5em"  # Slightly larger subheadings
REPORT_HEADING_COLOR = "#2c3e50"  # Formal dark blue
REPORT_SUBHEADING_COLOR = "#34495e"  # Slightly lighter complementary color

# Table Headers
REPORT_HEADER_BG_COLOR = "#34495e"  # Dark blue background for headers
REPORT_HEADER_TEXT_COLOR = "#ffffff"  # White text for contrast

# Table Rows
REPORT_ALT_ROW_BG_COLOR = "#f4f6f8"  # Light grey for alternating rows
REPORT_HOVER_ROW_BG = "#d5e0ed"  # Subtle blue for hover effect

# Backgrounds and Shadows
REPORT_MAIN_BG_COLOR = "#f8fafc"  # Very light blue for the main background
REPORT_TABLE_SHADOW_COLOR = "rgba(0,0,0,0.05)"  # Subtle shadow for depth
REPORT_TABLE_BORDER_RADIUS = "10px"  # Slightly rounded corners
REPORT_TABLE_BORDER_COLOR = "#bdc3c7"  # Light grey for borders
REPORT_TABLE_TEXT_COLOR = "#2c3e50"  # Match the formal heading color

# Container
REPORT_CONTAINER_MAX_WIDTH = "960px"  # Narrower for better readability
REPORT_CONTAINER_MARGIN = "0 auto"
REPORT_CONTAINER_PADDING = "40px"  # More spacious padding for elegance

# Body
REPORT_BODY_MARGIN = "0"
REPORT_BODY_PADDING = "0"

# Threshold Box
REPORT_THRESHOLD_BOX_BG_COLOR = "#ffffff"  # Pure white for a clean contrast
REPORT_THRESHOLD_BOX_BORDER_COLOR = "#dfe6e9"  # Softer grey border
REPORT_THRESHOLD_BOX_TEXT_COLOR = "#2c3e50"  # Consistent formal blue

# Threshold Section
REPORT_THRESHOLD_SECTION_BG_COLOR = "#f0f4f8"  # Gentle grey for thresholds
REPORT_THRESHOLD_SECTION_TEXT_COLOR = "#333"  # Standard text color

# Percentage Section
REPORT_PERCENTAGE_SECTION_BG_COLOR = "#ecf3fa"  # Light blue for emphasis
REPORT_PERCENTAGE_SECTION_TEXT_COLOR = "#2c3e50"

# Paragraphs
REPORT_PARAGRAPH_LINE_HEIGHT = "1.8em"  # Increased line height for better readability
REPORT_PARAGRAPH_MARGIN = "15px 0"  # Slightly more space between paragraphs

# Highlights
REPORT_BOLD_HIGHLIGHT_COLOR = "#2980b9"  # Vibrant blue for emphasis

REPORT_THRESHOLD_BOX_HOVER_BG_COLOR = "#f8fafc"  # Light blue for hover effect
REPORT_THRESHOLD_BOX_HOVER_SHADOW = "rgba(0,0,0,0.05)"
