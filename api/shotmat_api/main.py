import base64
from io import BytesIO
from fastapi import FastAPI, BackgroundTasks, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import threading
from PIL import Image
from .core.flux_txt2Img_request import FluxTxt2Im
from .core.flux_img2Img_request import FluxImg2Im

app = FastAPI()

# CORS middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Txt2ImgRequest(BaseModel):
    prompt: str

class Img2ImgRequest(BaseModel):
    prompt: str
    image: str  # Base64 encoded image
    strength: float = 0.7

flux_generator = None
flux_img_generator = None
model_loaded = False

def load_model():
    global flux_generator, flux_img_generator, model_loaded
    flux_generator = FluxTxt2Im(model="schnell")
    flux_img_generator = FluxImg2Im(pipeline=flux_generator.pipeline)
    model_loaded = True

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=load_model)
    thread.start()

@app.get("/health")
def health():
    return {"ok": True, "model_loaded": model_loaded}

@app.post("/txt2img")
def txt2img(request: Txt2ImgRequest):
    print(f"txt2img endpoint called with prompt: '{request.prompt}'")

    if not model_loaded:
        return Response(content='{"error": "Model not loaded yet"}', status_code=status.HTTP_503_SERVICE_UNAVAILABLE, media_type="application/json")

    image_b64 = flux_generator.generate(request.prompt)
    image_bytes = base64.b64decode(image_b64)
    
    return Response(content=image_bytes, media_type="image/png")

@app.post("/img2img")
def img2img(request: Img2ImgRequest):
    print(f"img2img endpoint called with prompt: '{request.prompt}' and strength: {request.strength}")

    if not model_loaded:
        return Response(content='{"error": "Model not loaded yet"}', status_code=status.HTTP_503_SERVICE_UNAVAILABLE, media_type="application/json")

    image_bytes = base64.b64decode(request.image)
    image = Image.open(BytesIO(image_bytes))

    image_b64 = flux_img_generator.generate(request.prompt, image, strength=request.strength)
    image_bytes = base64.b64decode(image_b64)
    return Response(content=image_bytes, media_type="image/png")