import base64
from io import BytesIO
from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel
from PIL import Image

router = APIRouter()

class Txt2ImgRequest(BaseModel):
    prompt: str

class Img2ImgRequest(BaseModel):
    prompt: str
    image: str  # Base64 encoded image
    strength: float = 0.7

class SuperResRequest(BaseModel):
    image: str # Base64 encoded image

@router.post("/txt2img")
def txt2img(request: Txt2ImgRequest, http_request: Request):
    print(f"txt2img endpoint called with prompt: '{request.prompt}'")

    if not http_request.app.state.model_loaded:
        return Response(content='{"error": "Model not loaded yet"}', status_code=status.HTTP_503_SERVICE_UNAVAILABLE, media_type="application/json")

    image_b64 = http_request.app.state.flux_generator.generate(request.prompt)
    image_bytes = base64.b64decode(image_b64)
    
    return Response(content=image_bytes, media_type="image/png")

@router.post("/img2img")
def img2img(request: Img2ImgRequest, http_request: Request):
    print(f"img2img endpoint called with prompt: '{request.prompt}' and strength: {request.strength}")

    if not http_request.app.state.model_loaded:
        return Response(content='{"error": "Model not loaded yet"}', status_code=status.HTTP_503_SERVICE_UNAVAILABLE, media_type="application/json")

    image_bytes = base64.b64decode(request.image)
    image = Image.open(BytesIO(image_bytes))

    image_b64 = http_request.app.state.flux_img_generator.generate(request.prompt, image, strength=request.strength)
    image_bytes = base64.b64decode(image_b64)
    return Response(content=image_bytes, media_type="image/png")

@router.post("/super-resolution")
def super_resolution(request: SuperResRequest, http_request: Request):
    print(f"super-resolution endpoint called.")

    if not http_request.app.state.model_loaded:
        return Response(content='{"error": "Model not loaded yet"}', status_code=status.HTTP_503_SERVICE_UNAVAILABLE, media_type="application/json")

    image_bytes = base64.b64decode(request.image)
    image = Image.open(BytesIO(image_bytes))

    image_b64 = http_request.app.state.tiposr_generator.upscale(image)
    image_bytes = base64.b64decode(image_b64)
    return Response(content=image_bytes, media_type="image/png")