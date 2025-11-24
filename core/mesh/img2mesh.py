import mlx.core as mx
import mlx.nn as nn

class ResidualBlock(nn.Module):
    """
    A standard residual block with two convolutional layers.
    """
    def __init__(self, channels: int):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)

    def __call__(self, x: mx.array) -> mx.array:
        residual = x
        out = self.conv1(x)
        out = self.relu(out)
        out = self.conv2(out)
        out = out + residual
        return out

class TipoSR(nn.Module):
    """
    An MLX implementation for a generic super-resolution model like TipoSR.
    This structure can be adapted to match the specific architecture of the
    model you are porting.
    """
    def __init__(self, upscale_factor: int = 4, num_channels: int = 64, num_blocks: int = 16, **kwargs):
        super().__init__()
        self.upscale_factor = upscale_factor

        # 1. Initial feature extraction layer
        self.conv_in = nn.Conv2d(in_channels=3, out_channels=num_channels, kernel_size=3, padding=1)

        # 2. A series of residual blocks for deep feature learning
        self.body = nn.Sequential(*[ResidualBlock(num_channels) for _ in range(num_blocks)])

        # 3. Upsampling block
        self.upsample = nn.Sequential(
            nn.Conv2d(num_channels, num_channels * (upscale_factor ** 2), kernel_size=3, padding=1),
            nn.PixelShuffle(upscale_factor),
        )

        # 4. Final reconstruction layer
        self.conv_out = nn.Conv2d(in_channels=num_channels, out_channels=3, kernel_size=3, padding=1)

    def __call__(self, x: mx.array) -> mx.array:
        x = self.conv_in(x)
        x = self.body(x)
        x = self.upsample(x)
        x = self.conv_out(x)
        return x