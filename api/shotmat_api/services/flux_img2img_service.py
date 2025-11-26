import base64
from io import BytesIO
import os
from typing import Dict, Any

import mlx.core as mx
import numpy as np
from PIL import Image
from tqdm import tqdm

# Assuming the service is used in an environment where shotmat_api is a package
# and we can do relative imports.
from shotmat.core.mlx.flux import FluxPipeline
from .shot_project_service import ProjectService, Shot

# Define a root for projects. In a real app, this would come from configuration.
# Using an environment variable is a common practice.
PROJECTS_ROOT = os.getenv("SHOTMAT_PROJECTS_ROOT", "/tmp/shotmat_projects")


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
        """
        Initializes the FluxImg2ImgService.

        Args:
            pipeline (FluxPipeline): An initialized FLUX pipeline instance.
        """
        self.pipeline = pipeline
        # The ProjectService needs the root directory for all projects.
        self.project_service = ProjectService(project_root=PROJECTS_ROOT)

    def generate(
        self,
        project_name: str,
        shot_id: str,
        prompt: str,
        image: Image.Image,
        strength: float = 0.7,
        steps: int = 10,
        guidance: float = 4.0,
        seed=None,
    ) -> Dict[str, Any]:
        """
        Generates an image from a prompt and an initial image, saves it,
        updates the project data, and returns the result.
        """
        # Prepare the input image
        latent_size = to_latent_size(image.size)
        resized_image = image.resize((latent_size[1] * 4, latent_size[0] * 4)) # The new AE has a downsampling factor of 4
        img_mx = (mx.array(np.array(resized_image.convert("RGB"))) / 255.0) * 2 - 1

        # Encode the image into the latent space
        init_latents = self.pipeline.ae.encode(img_mx[None])
        init_latents, init_latents_ids = self.pipeline._prepare_latent_images(init_latents)

        # Determine start step and add noise
        start_step = int(steps * strength)
        start_sigma = self.pipeline.sampler.timesteps(steps, init_latents.dtype)[start_step]
        
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
        x = (x[0] * 255).astype(mx.uint8)
        generated_image = Image.fromarray(np.array(x))
        
        # --- Save image to disk and update project data ---

        # 1. Save the generated image to a file
        buffered = BytesIO()
        generated_image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()

        # The project service handles file I/O and directory creation.
        # We need to find the shot to update its output URL.
        try:
            project = self.project_service.load_project(project_name)
            shot_to_update = next((s for s in project.shots if s.id == shot_id), None)
            if not shot_to_update:
                # If shot doesn't exist, create it. This is a reasonable fallback.
                shot_to_update = Shot(id=shot_id, input_text=prompt, mlx_args={}, output_url="")
                project.shots.append(shot_to_update)
        except FileNotFoundError:
            # If project doesn't exist, create it with the current shot
            shot_to_update = Shot(id=shot_id, input_text=prompt, mlx_args={}, output_url="")
            project = self.project_service.create_project_with_shot(project_name, shot_to_update)

        # Save the media file and get its URL
        media_url = self.project_service.save_shot_media(project_name, shot_id, image_bytes)
        shot_to_update.output_url = media_url

        # Persist the updated project data
        self.project_service.save_project(project)

        # 2. Prepare the response
        # Return the base64 encoded image for immediate display
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return {
            "project": project.dict(),
            "image_base64": img_str,
        }