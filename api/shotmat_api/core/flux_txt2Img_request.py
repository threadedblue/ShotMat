import base64
from io import BytesIO
import mlx.core as mx
import mlx.nn as nn
import numpy as np
from PIL import Image
from flux import FluxPipeline

def to_latent_size(image_size):
    h, w = image_size
    h = ((h + 15) // 16) * 16
    w = ((w + 15) // 16) * 16

    if (h, w) != image_size:
        print(
            f"Warning: The image dimensions need to be divisible by 16px. "
            f"Changing size to {h}x{w}."
        )

    return (h // 8, w // 8)

class FluxTxt2Img:
    def __init__(self, model="schnell", t5_padding=False):
        self.pipeline = FluxPipeline("flux-" + model, t5_padding=t5_padding)

    def generate(self, prompt, image_size=(1024, 1024), steps=2, guidance=4.0, n_images=1, decoding_batch_size=1, seed=None):
        # Make the generator
        latent_size = to_latent_size(image_size)
        latents = self.pipeline.generate_latents(
            prompt,
            n_images=n_images,
            num_steps=steps,
            latent_size=latent_size,
            guidance=guidance,
            seed=seed,
        )

        # First we get and eval the conditioning
        conditioning = next(latents)
        mx.eval(conditioning)

        # Actual denoising loop
        for x_t in latents:
            mx.eval(x_t)

        # Decode them into images
        decoded = []
        for i in range(0, n_images, decoding_batch_size):
            decoded.append(self.pipeline.decode(x_t[i : i + decoding_batch_size], latent_size))
            mx.eval(decoded[-1])

        # Arrange them on a grid
        x = mx.concatenate(decoded, axis=0)
        x = mx.pad(x, [(0, 0), (4, 4), (4, 4), (0, 0)])
        B, H, W, C = x.shape
        x = x.reshape(1, B // 1, H, W, C).transpose(0, 2, 1, 3, 4)
        x = x.reshape(1 * H, B // 1 * W, C)
        x = (x * 255).astype(mx.uint8)

        im = Image.fromarray(np.array(x))
        
        buffered = BytesIO()
        im.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return img_str
