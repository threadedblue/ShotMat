from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading

from .services.flux_txt2img_service import FluxTxt2ImgService
from .services.flux_img2img_service import FluxImg2ImgService
from .services.tiposr_img2mesh_service import TipoSRImg2MeshService
from .routes import generation

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Application startup: Loading models in a background thread.")
    app.state.model_loaded = False
    
    def load_model_thread():
        """Loads all models and attaches them to the app state."""
        flux_txt2img_service = FluxTxt2ImgService(model="schnell")
        app.state.flux_generator = flux_txt2img_service
        app.state.flux_img_generator = FluxImg2ImgService(pipeline=flux_txt2img_service.pipeline)
        app.state.tiposr_generator = TipoSRImg2MeshService(model_path="path/to/tiposr/weights.npz")
        app.state.model_loaded = True
        print("Models loaded successfully.")

    thread = threading.Thread(target=load_model_thread)
    thread.start()
    
    yield
    
    # Code to run on shutdown (e.g., cleanup resources)
    print("Application shutdown.")

app = FastAPI(lifespan=lifespan)

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

@app.get("/health")
def health():
    return {"ok": True, "model_loaded": app.state.model_loaded if hasattr(app.state, 'model_loaded') else False}

app.include_router(generation.router)