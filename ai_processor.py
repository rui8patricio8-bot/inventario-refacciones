import google.generativeai as genai
import json
from PIL import Image

# Configura tu llave de inteligencia artificial aquí
API_KEY = "AQ.Ab8RN6IhH2b-Ul7QjTwDsZgJlAqiCHEMoSdlKt-Tt-KHKMeNRg"
genai.configure(api_key=API_KEY)

def extract_data_from_image(image_file):
    try:
        # Abrir la imagen subida en la página web
        img = Image.open(image_file)
        
        # Usar el modelo visual más rápido de Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Darle la instrucción de qué buscar en la foto de tu refacción o factura
        prompt = """
        Analiza esta imagen de una refacción automotriz, ticket o factura.
        Extrae la siguiente información y devuélvela ÚNICAMENTE en formato JSON válido.
        No agregues saludos ni texto extra, solo el JSON con estas tres claves exactas:
        - "name": El nombre del producto o pieza.
        - "unit_cost": El precio o costo unitario en formato numérico (sin signos de peso ni comas). Si no lo encuentras, pon 0.0
        - "category": Clasifica el producto en la opción que mejor encaje de estas cuatro: "Iluminacion/Faros", "Aceites/Aditivos", "Calaveras", "Miscelaneos".
        """
        
        # Enviar la foto y la instrucción a la IA
        response = model.generate_content([prompt, img])
        
        # Limpiar la respuesta para que tu sistema la entienda perfectamente
        texto_limpio = response.text.strip().replace('```json', '').replace('```', '')
        datos = json.loads(texto_limpio)
        
        # Asegurar que el costo sea un número con decimales
        datos["unit_cost"] = float(datos.get("unit_cost", 0.0))
        
        return datos
        
    except Exception as e:
        print(f"Error procesando la imagen: {e}")
        # Si la foto sale borrosa o no se entiende, no se cae el sistema, devuelve esto:
        return {
            "name": "Error al leer imagen, ingresa manual",
            "unit_cost": 0.0,
            "category": "Miscelaneos"
        }
