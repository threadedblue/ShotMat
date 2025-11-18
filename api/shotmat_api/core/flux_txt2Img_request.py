import base64
from io import BytesIO
import mlx.core as mx
import mlx.nn as nn
import numpy as np
from PIL import Image
from tqdm import tqdm
from .flux import FluxPipeline

def to_latent_size(image_size):
    h, w = image_size
    h = ((h + 15) // 16) * 16
    w = ((w + 15) // 16) * 16

    if (h, w) != image_size:
        print(
            f"Warning: The image dimensions need to be divisible by 16px. "
            f"Changing size to {h}x{w}."
        )

    # The new autoencoder has a downsampling factor of 4
    return (h // 4, w // 4)

class FluxTxt2Im:
    def __init__(self, model="schnell", t5_padding=False):
        # The new pipeline takes the model name directly
        self.pipeline = FluxPipeline(name=f"flux-{model}", t5_padding=t5_padding)

    def generate(self, prompt, image_size=(1024, 1024), steps=2, guidance=4.0, n_images=1, decoding_batch_size=1, seed=None):
        latent_size = to_latent_size(image_size)

        # The new pipeline's generate_latents is a generator
        latents = self.pipeline.generate_latents(
            text=prompt,
            n_images=n_images,
            num_steps=steps,
            latent_size=latent_size,
            guidance=guidance,
            seed=seed,
        )
        
        # First, eval the conditioning
        conditioning = next(latents)
        mx.eval(conditioning)

        # Denoising loop to get the final latents
        # Use tqdm to show a progress bar in the console
        print("Starting denoising loop...")
        for x_t in tqdm(latents, total=steps, desc="Generating latents"):
            mx.eval(x_t)

        # Decode the final latents into an image
        # The new decode returns a value between 0 and 1
        x = self.pipeline.decode(x_t, latent_size=latent_size)
        x = (x * 255).astype(mx.uint8)

        # Assuming n_images is 1 for the API
        im = Image.fromarray(np.array(x[0]))
        
        buffered = BytesIO()
        im.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return img_str
