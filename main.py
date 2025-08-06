from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
import os
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use environment variable for Colab API URL
COLAB_API_URL = os.getenv("COLAB_API_URL", "https://your-placeholder-url")

class OutfitRequest(BaseModel):
    age: int
    gender: str
    occasion: str
    season: str
    style: str
    color: str


@app.post("/generate/")
async def generate_outfit(data: OutfitRequest):
    print("🚀 Intermediate backend /generate/ called with:", data)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("📦 Serializing data...")
            payload = data.model_dump()
            print("📦 Payload:", payload)

            colab_url = f"{COLAB_API_URL}/generate/"
            print("➡️ Sending to Colab:", colab_url)

            response = await client.post(colab_url, json=payload)
            print("⬅️ Colab response status:", response.status_code)
            print("⬅️ Colab response text:", response.text)

            result = response.json()
            print("✅ Final Colab JSON:", result)

            if "description" not in result or "image_base64" not in result:
                return JSONResponse(status_code=500, content={"error": "Invalid response from Colab"})

            return {
                "description": result["description"],
                "image_base64": result["image_base64"]
            }

    except Exception as e:
        import traceback
        print("❌ EXCEPTION:", traceback.format_exc()) 
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "trace": traceback.format_exc()}
        )
