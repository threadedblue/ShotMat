from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from .core.flux_txt2Img_request import FluxTxt2Img
import threading

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

flux_generator = None
model_loaded = False

def load_model():
    global flux_generator, model_loaded
#     flux_generator = FluxTxt2Img()
    model_loaded = True

@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=load_model)
    thread.start()

@app.get("/health")
def health():
    return {"ok": True, "model_loaded": model_loaded}

# @app.post("/txt2img")
# def txt2img(request: Txt2ImgRequest):
#     if not model_loaded:
#         return {"error": "Model not loaded yet"}, 503
        
#     image_data = flux_generator.generate(request.prompt)
#     return {"image": image_data}