from os import getenv
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import gradio as gr
import re

load_dotenv()

llm = ChatOpenAI(
    openai_api_key=getenv("OPENROUTER_API_KEY"),
    openai_api_base=getenv("OPENROUTER_BASE_URL"),
    model_name="openai/gpt-4o",
    model_kwargs={
        "extra_headers": {
            "Helicone-Auth": f"Bearer "+getenv("HELICONE_API_KEY")
        }
    },
)

# Cargar el contenido del archivo
def cargar_base_conocimiento(archivo):
    with open(archivo, "r", encoding="utf-8") as f:
        return f.read()

base_conocimiento = cargar_base_conocimiento("Chatbot Rags/rags Juegos.txt")

def buscar_respuesta(mensaje):
    """Busca información del juego en el archivo basado en la consulta del usuario."""
    mensaje_lower = mensaje.lower()

    # Expresión regular para extraer juegos completos
    juegos = re.findall(r'Juego \d+: .*?(?=--------------------------------------------------|$)', base_conocimiento, re.DOTALL)

    for juego in juegos:
        # Extraemos el nombre del juego usando regex
        titulo_match = re.search(r'Juego \d+: "(.*?)"', juego)
        if titulo_match:
            titulo = titulo_match.group(1).lower()  # Convertimos a minúsculas para comparación

            # Si el usuario menciona el nombre del juego en su mensaje, devolvemos la info
            if titulo in mensaje_lower:
                return juego.strip()
    
    return None  # Si no encuentra coincidencia, devuelve None

def chatbot(message, history):
    respuesta = buscar_respuesta(message)
    
    if respuesta:
        yield f"🎮 **Información del juego encontrado:**\n\n{respuesta}"  # Devolver la información del juego
    else:
        # Si no hay respuesta en el archivo, llamar a la API de OpenAI
        response = llm.stream([{"role": "user", "content": message}])

        partial_response = ""
        for chunk in response:
            if chunk and hasattr(chunk, 'content'):
                content = chunk.content
                if content is not None:
                    partial_response += content
                    yield partial_response

# Crear la interfaz del chatbot
demo = gr.ChatInterface(
    chatbot,
    chatbot=gr.Chatbot(height=400, type="messages"),
    textbox=gr.Textbox(placeholder="Escribe tu mensaje aquí...", container=False, scale=7),
    title="ChatBot de Videojuegos",
    description="Un asistente virtual sobre videojuegos.",
    theme="ocean",
    examples=[
        "Cuéntame sobre The Legend of Zelda: Breath of the Wild",
        "¿Qué me puedes decir de Fortnite?",
        "¿Cuál es la historia de Red Dead Redemption 2?",
    ],
    type="messages",
    editable=True,
    save_history=True,
)

# Lanzar la aplicación
if __name__ == "__main__":
    demo.queue().launch()
