import google.generativeai as genai
import json
from PIL import Image
import streamlit as st

# Aquí el código ya no tiene tu llave expuesta, va y la busca a la caja fuerte de Streamlit
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)

def extract_data_from_image(image_file):
    try:
        img = Image.open(image_file)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = """
        Analiza esta imagen de una refacción automotriz, ticket o factura.
        Extrae la siguiente información y devuélvela ÚNICAMENTE en formato JSON válido.
        No agregues saludos ni texto extra, solo el JSON con estas tres claves exactas:
        - "name": El nombre del producto o pieza.
        - "unit_cost": El precio o costo unitario en formato numérico (sin signos de peso ni comas). Si no lo encuentras, pon 0.0
        - "category": Clasifica el producto en la opción que mejor encaje de estas cuatro: "Iluminacion/Faros", "Aceites/Aditivos", "Calaveras", "Miscelaneos".
        """
        
        response = model.generate_content([prompt, img])
        
        texto_limpio = response.text.strip().replace('```json', '').replace('```', '')
        datos = json.loads(texto_limpio)
        
        datos["unit_cost"] = float(datos.get("unit_cost", 0.0))
        return datos
        
    except Exception as e:
        print(f"Error procesando la imagen: {e}")
        return {
            "name": "Error al leer imagen, ingresa manual",
            "unit_cost": 0.0,
            "category": "Miscelaneos"
        }
