# 🤖 API Chatbot – FastAPI

Esta API está desarrollada con **FastAPI** y actúa como un **intermediario entre un chatbot y el backend de Django (Tecnoshop)**.  
Permite recibir mensajes del chatbot, consultar productos en la API de Django y devolver resultados en formato JSON.

---

# ⚙️ Configuración del entorno

## 1️⃣ Crear e iniciar entorno virtual

Crea un entorno virtual dentro del proyecto:

```bash
py -m venv venv
```
Actívalo según tu sistema operativo, en Windows:
```bash
venv\Scripts\activate
```
En macOS / Linux:
```bash
source venv/bin/activate
```
## 2️⃣ Instalar dependencias
Instala los paquetes necesarios con:
```bash
pip install -r requirements.txt
```
## 3️⃣ Configurar variables de entorno
Crea un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido (modo pruebas):

```env
DJANGO_API_URL=http://localhost:8000/catalog
CHATBOT_API_KEY=mi_token_secreto_local
DJANGO_SERVICE_TOKEN=token_interno_django
ALLOWED_ORIGINS=http://localhost:8000
```

## 4️⃣ Estructura principal del proyecto
```bash
fastapi_chatbot/
│
├── main.py
├── .env
├── venv/
└── requirements.txt  (opcional)
```
## 5️⃣ Ejecutar el servidor FastAPI
Para iniciar el servidor local:
```bash
uvicorn main:app --reload --port 8001
```
Por defecto, el proyecto se ejecutará en:

👉 http://127.0.0.1:8001

### 🧠 Endpoint principal: POST `/chatbot/`
#### 🔹 Crear tunnel
Para conectar la API de FastAPI con **Landbot**, es necesario exponer tu servidor local a internet.  
Esto se logra utilizando **Cloudflare Tunnel**, una herramienta segura que genera una URL pública temporal para tu entorno local.

1. Instala **cloudflared** (si no lo tienes):
    ```bash
    npm install -g cloudflared
    ```
    o descárgalo desde https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation

2. Ejecuta el siguiente comando en la raíz de tu proyecto (donde corre tu API FastAPI):
    ```bash
    cloudflared tunnel --url http://localhost:8001
    ```
    Esto creará un túnel público hacia tu servidor local (por ejemplo, http://127.0.0.1:8001).

    Una vez iniciado, Cloudflare generará una URL temporal como esta:

    ```bash
    https://insured-eligibility-expressed-totals.trycloudflare.com
    ```
#### 🔹 Conectar la API con Landbot
En tu bot de Landbot, agrega un bloque de Webhook.

Configura el método como POST.

En el campo de URL del Webhook, pega la dirección pública generada por Cloudflare, seguida del endpoint /chatbot/.

Ejemplo:
```bash
https://insured-eligibility-expressed-totals.trycloudflare.com/chatbot/
```
Ahora, Landbot podrá enviar mensajes al endpoint /chatbot/ de tu API FastAPI, que internamente se comunica con tu backend de Django.


#### 🔹 Descripción
Recibe un mensaje del chatbot, consulta la API de productos de Django y devuelve una lista de coincidencias.

🔹 Encabezados requeridos
| Header | Valor esperado |
|------------|------------|
|`x-api-key`|Tu valor de `CHATBOT_API_KEY` del archivo `.env`     | Dato 3     |

#### 🔹 Cuerpo de la solicitud (JSON)
```json
{
  "mensaje": "laptop",
  "user_id": "usuario_123"
}
```
#### 🔹 Ejemplo de respuesta (éxito)
```json
{
  "productos": [
    {
      "id": 5,
      "nombre": "Laptop Lenovo IdeaPad",
      "precio": 2400.99,
      "imagen": "http://localhost:8000/media/laptops/lenovo.jpg",
      "categoria": "Laptops"
    }
  ],
  "mensaje": "Tenemos 1 producto(s) relacionados con tu búsqueda."
}
```
#### 🔹 Ejemplo de respuesta (sin resultados)
```json
{
  "productos": [],
  "mensaje": "No encontré productos relacionados con tu búsqueda 😕."
}
```
🚨 Manejo de errores\
- **401 – Invalid API Key** → La clave de acceso enviada en el header no coincide con la definida en .env.
- **500 – Error de conexión** → No se pudo comunicar con la API de Django.
- **Empty result** → No se encontraron productos que coincidan con la búsqueda.

# 🧩 Lógica general (resumen del código)
- Carga las variables de entorno desde `.env` con `python-dotenv`.
- Usa **httpx.AsyncClient** para hacer peticiones asíncronas a la API Django (`/api/productos/`).
- Filtra los productos por el término buscado (`?q=mensaje`).
- Devuelve los productos formateados y un mensaje amigable para el chatbot.