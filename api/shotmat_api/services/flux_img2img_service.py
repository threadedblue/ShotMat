import base64
from io import BytesIO

import mlx.core as mx
import numpy as np
from PIL import Image
from tqdm import tqdm

from .flux_pipeline import FluxPipeline


def to_latent_size(image_size):
    h, w = image_size
    h = ((h + 15) // 16) * 16
    w = ((w + 15) // 16) * 16

    if (h, w) != image_size:
        print(
            f"Warning: The image dimensions need to be divisible by 16px. "
            f"Changing size to {h}x{w}."
        )

    return (h // 4, w // 4)


class FluxImg2ImgService:
    def __init__(self, pipeline: FluxPipeline):
        self.pipeline = pipeline

    def generate(self, prompt: str, image: Image.Image, strength: float = 0.7, steps: int = 10, guidance: float = 4.0, seed=None):
        # Prepare the input image
        latent_size = to_latent_size(image.size)
        image = image.resize(latent_size)
        img_mx = (mx.array(np.array(image.convert("RGB"))) / 255.0) * 2 - 1

        # Encode the image into the latent space
        init_latents = self.pipeline.ae.encode(img_mx[None])
        init_latents, init_latents_ids = self.pipeline._prepare_latent_images(init_latents)

        # Determine start step and add noise
        start_step = int(steps * strength)
        start_sigma = self.pipeline.sampler.timesteps(steps, init_latents.shape[1])[start_step]
        
        if seed is not None:
            mx.random.seed(seed)
        noise = mx.random.normal(init_latents.shape, dtype=init_latents.dtype)
        
        # Start generation from the noised initial latent
        latents_t = self.pipeline.sampler.add_noise(init_latents, mx.array(start_sigma), noise=noise)

        # Get text conditioning
        t5_tokens, clip_tokens = self.pipeline.tokenize(prompt)
        txt, txt_ids, vec = self.pipeline._prepare_conditioning(1, t5_tokens, clip_tokens)

        # Run the denoising loop from the start_sigma
        print(f"Starting img2img denoising loop for {steps - start_step} steps...")
        denoising_generator = self.pipeline._denoising_loop(
            latents_t, init_latents_ids, txt, txt_ids, vec, 
            num_steps=steps, guidance=guidance, start=start_sigma
        )

        for x_t in tqdm(denoising_generator, total=steps, initial=start_step, desc="Denoising"):
            mx.eval(x_t)

        # Decode the final latents into an image
        x = self.pipeline.decode(x_t, latent_size=latent_size)
        x = (x * 255).astype(mx.uint8)
        im = Image.fromarray(np.array(x[0]))
        
        buffered = BytesIO()
        im.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return img_str