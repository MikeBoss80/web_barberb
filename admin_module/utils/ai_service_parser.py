import os
import io
import json
import pdfplumber
from PIL import Image
import pytesseract
import google.generativeai as genai

#OCR usando pytesseract o pdfplumber.

#Enviar el texto extraído a Gemini API para obtener estructura organizada de servicios.

#Retornar una lista de diccionarios de servicios.

# Configurar la clave de la API de Gemini
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


def extract_text(file):
    """
    Extrae texto de un archivo PDF o imagen utilizando OCR.
    """
    text = ""
    file_name = file.name.lower()

    if file_name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif any(file_name.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"]):
        image = Image.open(file)
        text = pytesseract.image_to_string(image, lang="spa")
    else:
        raise ValueError("Formato de archivo no compatible. Sube PDF o imagen.")

    if not text.strip():
        raise ValueError("No se pudo extraer texto del archivo.")

    return text

def extract_json_from_response(content):
    """
    Extrae un JSON de la respuesta de Gemini.
    """
    try:
        # Buscar el primer bloque de JSON en la respuesta
        start = content.find("{")
        end = content.rfind("}") + 1
        json_str = content[start:end]
        data = json.loads(json_str)
        return data
    except Exception as e:
        raise ValueError(f"No se pudo parsear la respuesta de Gemini: {e}")

def extract_services_from_file(file):
    """
    Flujo completo: OCR -> Gemini -> Extraer JSON de servicios.
    Retorna una lista de servicios para cargar a la BD.
    """
    text = extract_text(file)

    prompt = f"""
Extrae los servicios de la siguiente carta de servicios de barbería. Devuelve estrictamente en formato JSON con el siguiente esquema:
[
  {{
    "name_service": "Nombre del servicio",
    "description_service": "Descripción del servicio",
    "price_service": 15000,
    "duration": 30
  }},
  ...
]

Asegúrate de incluir precio como número entero en pesos COP y duración como número entero en minutos. Si no hay duración, estímalo según lo usual. Aquí está el texto:

{text}
"""

    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content(prompt)

    data = extract_json_from_response(response.text)

    # Validación de estructura
    if not isinstance(data, list):
        raise ValueError("La respuesta de Gemini no es una lista de servicios.")

    for service in data:
        if not all(key in service for key in ["name", "description", "price", "duration"]):
            raise ValueError("Faltan campos en algunos servicios generados por Gemini.")

    return data


def extract_services_from_file(file):
    #1 Extraer tecto con OCR o pdfplumber
    text = extract_text(file)

    #2 Usar Gemini API
    client= GeminiClient()
    prompt = f"""
    Analiza el todo el texto de la imagen o documento y devuelve una lista JSON de servicios con:
    - name_service
    - description_service
    - prince_service
    - duration (si no brinda este dato puedes recomendar o intuir cuando demoraria)
    
    Texto:
    {text}
    """

    response = client.chat.completions.create(
        model="gemini-1.5-pro-latest",
        messages=[{"role": "user", "content": prompt}]
    )

    #Parsear el JSON de la respuesta
    data = extract_json_from_response(response.choices[0].message.content)

    return data
