# Copyright © 2024 Apple Inc.

from typing import Tuple

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_unflatten
from tqdm import tqdm

from .flux import LoRALinear
from .flux import FluxSampler
from .flux import (
    load_ae,
    load_clip,
    load_clip_tokenizer,
    load_flow_model,
    load_t5,
    load_t5_tokenizer,
)


class FluxPipeline:
    def __init__(self, name: str, t5_padding: bool = True):
        self.dtype = mx.bfloat16
        self.name = name
        self.t5_padding = t5_padding

        self.ae = load_ae(name)
        self.flow = load_flow_model(name)
        self.clip = load_clip(name)
        self.clip_tokenizer = load_clip_tokenizer(name)
        self.t5 = load_t5(name)
        self.t5_tokenizer = load_t5_tokenizer(name)
        self.sampler = FluxSampler(name)

    def ensure_models_are_loaded(self):
        mx.eval(
            self.ae.parameters(),
            self.flow.parameters(),
            self.clip.parameters(),
            self.t5.parameters(),
        )

    def reload_text_encoders(self):
        self.t5 = load_t5(self.name)
        self.clip = load_clip(self.name)

    def tokenize(self, text):
        t5_tokens = self.t5_tokenizer.encode(text, pad=self.t5_padding)
        clip_tokens = self.clip_tokenizer.encode(text)
        return t5_tokens, clip_tokens

    def _prepare_latent_images(self, x):
        b, h, w, c = x.shape

        # Pack the latent image to 2x2 patches
        x = x.reshape(b, h // 2, 2, w // 2, 2, c)
        x = x.transpose(0, 1, 3, 5, 2, 4).reshape(b, h * w // 4, c * 4)

        # Create positions ids used to positionally encode each patch. Due to
        # the way RoPE works, this results in an interesting positional
        # encoding where parts of the feature are holding different positional
        # information. Namely, the first part holds information independent of
        # the spatial position (hence 0s), the 2nd part holds vertical spatial
        # information and the last one horizontal.
        i = mx.zeros((h // 2, w // 2), dtype=mx.int32)
        j, k = mx.meshgrid(mx.arange(h // 2), mx.arange(w // 2), indexing="ij")
        x_ids = mx.stack([i, j, k], axis=-1)
        x_ids = mx.repeat(x_ids.reshape(1, h * w // 4, 3), b, 0)

        return x, x_ids

    def _prepare_conditioning(self, n_images, t5_tokens, clip_tokens):
        # Prepare the text features
        txt = self.t5(t5_tokens)
        if len(txt) == 1 and n_images > 1:
            txt = mx.broadcast_to(txt, (n_images, *txt.shape[1:]))
        txt_ids = mx.zeros((n_images, txt.shape[1], 3), dtype=mx.int32)

        # Prepare the clip text features
        vec = self.clip(clip_tokens).pooled_output
        if len(vec) == 1 and n_images > 1:
            vec = mx.broadcast_to(vec, (n_images, *vec.shape[1:]))

        return txt, txt_ids, vec

    def _denoising_loop(
        self,
        x_t,
        x_ids,
        txt,
        txt_ids,
        vec,
        num_steps: int = 35,
        guidance: float = 4.0,
        start: float = 1,
        stop: float = 0,
    ):
        B = len(x_t)

        def scalar(x):
            return mx.full((B,), x, dtype=self.dtype)

        guidance = scalar(guidance)
        timesteps = self.sampler.timesteps(
            num_steps,
            x_t.shape[1],
            start=start,
            stop=stop,
        )
        for i in range(num_steps):
            t = timesteps[i]
            t_prev = timesteps[i + 1]

            pred = self.flow(
                img=x_t,
                img_ids=x_ids,
                txt=txt,
                txt_ids=txt_ids,
                y=vec,
                timesteps=scalar(t),
                guidance=guidance,
            )
            x_t = self.sampler.step(pred, x_t, t, t_prev)

            yield x_t

    def generate_latents(
        self,
        text: str,
        n_images: int = 1,
        num_steps: int = 35,
        guidance: float = 4.0,
        latent_size: Tuple[int, int] = (64, 64),
        seed=None,
    ):
        # Set the PRNG state
        if seed is not None:
            mx.random.seed(seed)

        # Create the latent variables
        x_T = self.sampler.sample_prior((n_images, *latent_size, 16), dtype=self.dtype)
        x_T, x_ids = self._prepare_latent_images(x_T)

        # Get the conditioning
        t5_tokens, clip_tokens = self.tokenize(text)
        txt, txt_ids, vec = self._prepare_conditioning(n_images, t5_tokens, clip_tokens)

        # Yield the conditioning for controlled evaluation by the caller
        yield (x_T, x_ids, txt, txt_ids, vec)

        # Yield the latent sequences from the denoising loop
        yield from self._denoising_loop(
            x_T, x_ids, txt, txt_ids, vec, num_steps=num_steps, guidance=guidance
        )

    def decode(self, x, latent_size: Tuple[int, int] = (64, 64)):
        h, w = latent_size
        x = x.reshape(len(x), h // 2, w // 2, -1, 2, 2)
        x = x.transpose(0, 1, 4, 2, 5, 3).reshape(len(x), h, w, -1)
        x = self.ae.decode(x)
        return mx.clip(x + 1, 0, 2) * 0.5

    def generate_images(
        self,
        text: str,
        n_images: int = 1,
        num_steps: int = 35,
        guidance: float = 4.0,
        latent_size: Tuple[int, int] = (64, 64),
        seed=None,
        reload_text_encoders: bool = True,
        progress: bool = True,
    ):
        latents = self.generate_latents(
            text, n_images, num_steps, guidance, latent_size, seed
        )
        mx.eval(next(latents))

        if reload_text_encoders:
            self.reload_text_encoders()

        for x_t in tqdm(latents, total=num_steps, disable=not progress, leave=True):
            mx.eval(x_t)

        images = []
        for i in tqdm(range(len(x_t)), disable=not progress, desc="generate images"):
            images.append(self.decode(x_t[i : i + 1]))
            mx.eval(images[-1])
        images = mx.concatenate(images, axis=0)
        mx.eval(images)

        return images

    def training_loss(
        self,
        x_0: mx.array,
        t5_features: mx.array,
        clip_features: mx.array,
        guidance: mx.array,
    ):
        # Get the text conditioning
        txt = t5_features
        txt_ids = mx.zeros(txt.shape[:-1] + (3,), dtype=mx.int32)
        vec = clip_features

        # Prepare the latent input
        x_0, x_ids = self._prepare_latent_images(x_0)

        # Forward process
        t = self.sampler.random_timesteps(*x_0.shape[:2], dtype=self.dtype)
        eps = mx.random.normal(x_0.shape, dtype=self.dtype)
        x_t = self.sampler.add_noise(x_0, t, noise=eps)
        x_t = mx.stop_gradient(x_t)

        # Do the denoising
        pred = self.flow(
            img=x_t,
            img_ids=x_ids,
            txt=txt,
            txt_ids=txt_ids,
            y=vec,
            timesteps=t,
            guidance=guidance,
        )

        return (pred + x_0 - eps).square().mean()

    def linear_to_lora_layers(self, rank: int = 8, num_blocks: int = -1):
        """Swap the linear layers in the transformer blocks with LoRA layers."""
        all_blocks = self.flow.double_blocks + self.flow.single_blocks
        all_blocks.reverse()
        num_blocks = num_blocks if num_blocks > 0 else len(all_blocks)
        for i, block in zip(range(num_blocks), all_blocks):
            loras = []
            for name, module in block.named_modules():
                if isinstance(module, nn.Linear):
                    loras.append((name, LoRALinear.from_base(module, r=rank)))
            block.update_modules(tree_unflatten(loras))

    def fuse_lora_layers(self):
        fused_layers = []
        for name, module in self.flow.named_modules():
            if isinstance(module, LoRALinear):
                fused_layers.append((name, module.fuse()))
        self.flow.update_modules(tree_unflatten(fused_layers))
import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_unflatten
from PIL import Image
from tqdm import tqdm

from .transformer import DiT, IDM, T5


@dataclass
class FluxConfig:
    """
    Configuration for the FLUX model.

    Args:
        text_hidden_size (int): The hidden size of the T5 text encoder.
        text_heads (int): The number of attention heads in the T5 text encoder.
        text_layers (int): The number of layers in the T5 text encoder.
        text_mlp_dim (int): The MLP dimension of the T5 text encoder.
        text_vocab_size (int): The vocabulary size of the T5 text encoder.
        img_hidden_size (int): The hidden size of the DiT image model.
        img_heads (int): The number of attention heads in the DiT image model.
        img_layers (int): The number of layers in the DiT image model.
        img_patch_size (int): The patch size of the DiT image model.
        img_in_channels (int): The number of input channels of the DiT image model.
        clip_img_size (int): The size of the CLIP image embeddings.
        clip_img_channels (int): The number of channels of the CLIP image embeddings.
        clip_patch_size (int): The patch size of the CLIP image embeddings.
        idm_hidden_size (int): The hidden size of the IDM model.
    """

    text_hidden_size: int = 2048
    text_heads: int = 32
    text_layers: int = 34
    text_mlp_dim: int = 5120
    text_vocab_size: int = 32128
    img_hidden_size: int = 2048
    img_heads: int = 32
    img_layers: int = 34
    img_patch_size: int = 2
    img_in_channels: int = 16
    clip_img_size: int = 768
    clip_img_channels: int = 1280
    clip_patch_size: int = 14
    idm_hidden_size: int = 2048


class Flux(nn.Module):
    """
    The FLUX model.

    Args:
        config (FluxConfig): The configuration for the FLUX model.
    """

    def __init__(self, config: FluxConfig):
        super().__init__()
        self.text_model = T5(
            config.text_hidden_size,
            config.text_heads,
            config.text_layers,
            config.text_mlp_dim,
            config.text_vocab_size,
        )
        self.img_model = DiT(
            config.img_hidden_size,
            config.img_heads,
            config.img_layers,
            config.img_patch_size,
            config.img_in_channels,
        )
        self.idm = IDM(
            config.img_hidden_size,
            config.clip_img_size,
            config.clip_img_channels,
            config.clip_patch_size,
            config.idm_hidden_size,
        )

    def __call__(
        self,
        txt_tokens: mx.array,
        img_tokens: mx.array,
        clip_tokens: mx.array,
        time: mx.array,
    ) -> mx.array:
        text_embeddings = self.text_model(txt_tokens)
        text_embeddings_pooled = text_embeddings.mean(axis=1)
        img_embeddings = self.idm(img_tokens, clip_tokens, text_embeddings_pooled)
        return self.img_model(img_embeddings, time)

    @staticmethod
    def from_single_weights(text_weights, img_weights, idm_weights):
        config = FluxConfig()
        model = Flux(config)
        model.text_model.update(tree_unflatten(list(text_weights.items())))
        model.img_model.update(tree_unflatten(list(img_weights.items())))
        model.idm.update(tree_unflatten(list(idm_weights.items())))
        return model


class FluxPipeline:
    def __init__(self, model_path: str, t5_padding: bool = False):
        self.config = FluxConfig()
        self.model = Flux(self.config)
        self.model.load_weights(model_path + "/weights.npz")
        self.model.eval()

        from transformers import AutoTokenizer, T5Tokenizer

        self.tokenizer = T5Tokenizer.from_pretrained(
            "google/flan-t5-xl", legacy=False, cache_dir=model_path
        )
        self.t5_padding = t5_padding

        self.vae = self._load_vae(model_path)

    def _load_vae(self, model_path: str):
        # TODO: Replace with MLX VAE
        from diffusers import AutoencoderKL

        vae = AutoencoderKL.from_pretrained(
            "stabilityai/sdxl-vae", cache_dir=model_path
        )
        return vae

    def _text_to_tokens(self, text: str, max_length: int = 512):
        tokens = self.tokenizer(
            text,
            return_tensors="np",
            max_length=max_length,
            padding="max_length" if self.t5_padding else "do_not_pad",
            truncation=True,
        ).input_ids
        return mx.array(tokens)

    def _get_guidance_scale_embedding(self, w, embedding_dim=256):
        # https://github.com/huggingface/diffusers/blob/v0.28.0/src/diffusers/pipelines/wuerstchen/pipeline_wuerstchen_prior.py#L1039
        w = mx.array([w])
        w_embedding = mx.zeros((1, embedding_dim))
        w_embedding[:, :1] = mx.sin(w * math.pi / 2)
        w_embedding[:, 1:2] = mx.cos(w * math.pi / 2)
        return w_embedding

    def generate_latents(
        self,
        prompt: str,
        n_images: int = 1,
        num_steps: int = 20,
        latent_size: tuple = (128, 128),
        guidance: float = 4.0,
        seed: int = 0,
    ):
        mx.random.seed(seed)

        # TODO: Add support for negative prompt
        tokens = self._text_to_tokens(prompt)
        tokens = mx.concatenate([tokens] * n_images, axis=0)

        # TODO: Add support for CLIP image guidance
        clip_img = mx.zeros((n_images, 1, self.config.clip_img_channels))

        # TODO: Add support for guidance
        guidance_embedding = self._get_guidance_scale_embedding(guidance)
        guidance_embedding = mx.concatenate([guidance_embedding] * n_images, axis=0)

        # TODO: Add support for different schedulers
        timesteps = mx.linspace(1, 0, num_steps + 1)
        sigmas = timesteps  # Rectified flow

        # Yield the conditioning so it can be cached
        yield (tokens, clip_img, guidance_embedding)

        latents = mx.random.normal(
            (n_images, latent_size[0], latent_size[1], self.config.img_in_channels)
        )

        for i in tqdm(range(num_steps)):
            # TODO: Add support for guidance
            sigma = sigmas[i]
            sigma_next = sigmas[i + 1]
            time = mx.array([sigma] * n_images)

            # Denoise
            pred = self.model(tokens, latents, clip_img, time)

            # Scheduler step
            d = (latents - pred) / sigma
            dt = sigma_next - sigma
            latents = latents + d * dt

            yield latents

    def decode(self, latents: mx.array, latent_size: tuple):
        # TODO: Replace with MLX VAE
        import torch

        latents = latents.reshape(
            -1, self.config.img_in_channels, latent_size[0], latent_size[1]
        )
        latents = torch.from_numpy(np.array(latents))
        decoded = self.vae.decode(latents / self.vae.config.scaling_factor).sample
        return mx.array(decoded.numpy()).transpose(0, 2, 3, 1)