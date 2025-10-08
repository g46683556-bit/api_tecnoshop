from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

DJANGO_API_URL = os.getenv("DJANGO_API_URL")
CHATBOT_API_KEY = os.getenv("CHATBOT_API_KEY")


class ChatbotInput(BaseModel):
    mensaje: str
    user_id: str | None = None


@app.post("/chatbot/")
async def chatbot_endpoint(data: ChatbotInput, x_api_key: str = Header(None)):
    if x_api_key != CHATBOT_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DJANGO_API_URL}/api/productos/?q={data.mensaje}")
            response.raise_for_status()
            productos = response.json()
    except Exception as e:
        print("Error al conectar con Django:", e)
        return {"error": "Error de conexión con el servicio de productos. Intenta más tarde."}

    if not productos:
        return {"productos": [], "mensaje": "No encontré productos relacionados con tu búsqueda 😕."}

    productos_formateados = [
        {
            "id": p["id"],
            "nombre": p["name"],
            "precio": p["price"],
            "imagen": p["image_url"],
            "categoria": p["category"],
        }
        for p in productos
    ]

    return {
        "productos": productos_formateados,
        "mensaje": f"Tenemos {len(productos_formateados)} producto(s) relacionados con tu búsqueda."
    }
